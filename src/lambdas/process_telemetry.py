"""Lambda de procesamiento (capas Bronze y Silver).

Disparada por la regla de AWS IoT Core. Por cada mensaje de telemetría:
  1. Guarda el mensaje original en S3 (Bronze).
  2. Escribe el registro validado en DynamoDB (Silver), de forma idempotente.
  3. Actualiza el último estado del dispositivo sin dejar que un dato atrasado
     reemplace a uno más reciente.
  4. Publica una alerta en SNS si la batería es baja o la corriente es anormal.
"""
import json
import logging
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
sns = boto3.client("sns")
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

BUCKET = os.environ["BUCKET_NAME"]
TOPIC_ARN = os.environ["ALERT_TOPIC_ARN"]
BATTERY_MIN = float(os.environ.get("BATTERY_MIN_PCT", "20"))
CURRENT_MAX = float(os.environ.get("MOTOR_CURRENT_MAX_A", "5.0"))

REQUIRED = ("device_id", "event_id", "ts")


def _alerts(item):
    alerts = []
    battery = item.get("battery_pct")
    current = item.get("motor_current_a")
    if battery is not None and float(battery) < BATTERY_MIN:
        alerts.append(f"Batería baja: {battery} % (mínimo {BATTERY_MIN} %)")
    if current is not None and float(current) > CURRENT_MAX:
        alerts.append(f"Corriente anormal: {current} A (máximo {CURRENT_MAX} A)")
    return alerts


def handler(event, context):
    missing = [k for k in REQUIRED if k not in event]
    if missing:
        logger.error("Mensaje inválido, faltan campos: %s", missing)
        return {"status": "invalid"}

    device_id = str(event["device_id"])
    ts = str(event["ts"])  # ISO 8601 en UTC, p. ej. 2026-10-23T18:00:00Z
    event_id = str(event["event_id"])

    # --- Bronze: mensaje original, organizado por dispositivo y fecha ---
    key = f"telemetria/maquinas/{device_id}/{ts[:10]}/{ts}_{event_id}.json"
    s3.put_object(
        Bucket=BUCKET, Key=key, Body=json.dumps(event).encode("utf-8"),
        ContentType="application/json",
    )

    # --- Silver: historial idempotente (mismo event_id => no se duplica) ---
    item = json.loads(json.dumps(event), parse_float=Decimal)
    item["sk"] = f"{ts}#{event_id}"
    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(device_id)",
        )
    except ClientError as err:
        if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.info("Evento duplicado ignorado: %s", event_id)
            return {"status": "duplicate"}
        raise

    # --- Último estado: un dato atrasado no reemplaza a uno más reciente ---
    latest = dict(item, sk="LATEST", last_ts=ts, alerted=False)
    try:
        table.put_item(
            Item=latest,
            ConditionExpression="attribute_not_exists(device_id) OR last_ts < :t",
            ExpressionAttributeValues={":t": ts},
        )
    except ClientError as err:
        if err.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise
        logger.info("Dato histórico (no reemplaza el último estado): %s", ts)

    # --- Alertas ---
    for text in _alerts(event):
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=f"Alerta robot {device_id}"[:100],
            Message=f"{device_id} @ {ts}: {text}",
        )
    return {"status": "ok", "key": key}
