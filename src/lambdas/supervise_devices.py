"""Lambda de supervisión.

La activa EventBridge cada minuto. Revisa el último estado de cada dispositivo
y publica una alerta en SNS si lleva más de TIMEOUT_SECONDS sin reportar.
Cada desconexión se avisa una sola vez (atributo `alerted`) hasta que el
dispositivo vuelva a enviar datos.
"""
import logging
import os
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client("sns")
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
TOPIC_ARN = os.environ["ALERT_TOPIC_ARN"]
TIMEOUT_SECONDS = int(os.environ.get("TIMEOUT_SECONDS", "60"))


def _parse(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def handler(event, context):
    now = datetime.now(timezone.utc)
    response = table.scan(FilterExpression=Attr("sk").eq("LATEST"))
    items = response["Items"]
    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression=Attr("sk").eq("LATEST"),
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response["Items"])

    notified = 0
    for item in items:
        silence = (now - _parse(item["last_ts"])).total_seconds()
        if silence > TIMEOUT_SECONDS and not item.get("alerted", False):
            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject=f"Sin datos: {item['device_id']}"[:100],
                Message=(f"{item['device_id']} lleva {int(silence)} s sin reportar "
                         f"(último dato: {item['last_ts']})."),
            )
            table.update_item(
                Key={"device_id": item["device_id"], "sk": "LATEST"},
                UpdateExpression="SET alerted = :t",
                ExpressionAttributeValues={":t": True},
            )
            notified += 1
    logger.info("Dispositivos revisados: %d, alertas: %d", len(items), notified)
    return {"checked": len(items), "alerts": notified}
