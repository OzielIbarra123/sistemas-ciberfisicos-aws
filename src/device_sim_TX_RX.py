"""Simulador de dispositivo (robot móvil) para AWS IoT Core: TX y RX por MQTT.

TX: publica telemetría en  almacen/robots/<device_id>/telemetria
RX: escucha comandos en    almacen/robots/<device_id>/cmd
    y responde un acuse en almacen/robots/<device_id>/ack

Si se pierde la conexión, la telemetría se guarda localmente (hasta 30 minutos)
y se reenvía al reconectar, marcada con "replay": true. Cada mensaje lleva un
`event_id` único para que la nube evite duplicados.

Uso:
    python device_sim_TX_RX.py --endpoint <prefijo>-ats.iot.us-east-2.amazonaws.com \
        --cert robot-01.cert.pem --key robot-01.private.key --ca AmazonRootCA1.pem \
        --device-id robot-01 --rate 1 --duration 60
"""
import argparse
import json
import random
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BUFFER_MINUTES = 30


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RobotSim:
    def __init__(self, args):
        self.args = args
        self.device_id = args.device_id
        self.topic_tx = f"almacen/robots/{self.device_id}/telemetria"
        self.topic_cmd = f"almacen/robots/{self.device_id}/cmd"
        self.topic_ack = f"almacen/robots/{self.device_id}/ack"
        self.buffer = deque(maxlen=int(BUFFER_MINUTES * 60 * max(args.rate, 1)))
        self.connected = threading.Event()
        self.state = {"x": 0.0, "y": 0.0, "battery": 100.0, "state": "RUNNING"}

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.device_id)
        self.client.tls_set(ca_certs=args.ca, certfile=args.cert, keyfile=args.key)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    # ---------- RX ----------
    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"[RX] conectado ({reason_code}); suscrito a {self.topic_cmd}")
        client.subscribe(self.topic_cmd, qos=1)
        self.connected.set()

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        print(f"[RX] desconectado ({reason_code}); se almacenará telemetría local")
        self.connected.clear()

    def on_message(self, client, userdata, msg):
        print(f"[RX] comando recibido: {msg.payload.decode(errors='replace')}")
        try:
            cmd = json.loads(msg.payload)
        except json.JSONDecodeError:
            cmd = {}
        if cmd.get("command") == "stop":
            self.state["state"] = "STOPPED"
        elif cmd.get("command") == "start":
            self.state["state"] = "RUNNING"
        ack = {"device_id": self.device_id, "ts": utc_now(), "ack": cmd.get("command"),
               "state": self.state["state"]}
        client.publish(self.topic_ack, json.dumps(ack), qos=1)

    # ---------- TX ----------
    def sample(self):
        s = self.state
        if s["state"] == "RUNNING":
            s["x"] += random.uniform(-0.2, 0.3)
            s["y"] += random.uniform(-0.2, 0.3)
            s["battery"] = max(0.0, s["battery"] - random.uniform(0.0, 0.05))
        current = random.gauss(2.0, 0.4) if s["state"] == "RUNNING" else 0.1
        if random.random() < 0.01:  # anomalía ocasional para probar las alertas
            current = random.uniform(5.5, 7.0)
        return {
            "device_id": self.device_id,
            "event_id": str(uuid.uuid4()),
            "ts": utc_now(),
            "x": round(s["x"], 3), "y": round(s["y"], 3),
            "speed_mps": round(random.uniform(0.2, 0.6), 3) if s["state"] == "RUNNING" else 0.0,
            "battery_pct": round(s["battery"], 2),
            "motor_current_a": round(max(current, 0.0), 3),
            "state": s["state"],
        }

    def publish(self, payload):
        self.client.publish(self.topic_tx, json.dumps(payload), qos=1)

    def run(self):
        self.client.connect_async(self.args.endpoint, 8883, keepalive=30)
        self.client.loop_start()
        end = time.time() + self.args.duration if self.args.duration else None
        period = 1.0 / self.args.rate
        try:
            while end is None or time.time() < end:
                payload = self.sample()
                if self.connected.is_set():
                    while self.buffer:  # reenviar lo acumulado durante la desconexión
                        old = self.buffer.popleft()
                        old["replay"] = True
                        self.publish(old)
                    self.publish(payload)
                    print(f"[TX] {payload['ts']} bat={payload['battery_pct']}% "
                          f"I={payload['motor_current_a']} A")
                else:
                    self.buffer.append(payload)
                    print(f"[TX] sin conexión; en buffer: {len(self.buffer)}")
                time.sleep(period)
        except KeyboardInterrupt:
            pass
        finally:
            self.client.loop_stop()
            self.client.disconnect()


def main():
    p = argparse.ArgumentParser(description="Simulador TX/RX de robot para AWS IoT Core")
    p.add_argument("--endpoint", required=True, help="Endpoint de IoT Core (ATS)")
    p.add_argument("--cert", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--ca", required=True, help="AmazonRootCA1.pem")
    p.add_argument("--device-id", default="robot-01")
    p.add_argument("--rate", type=float, default=1.0, help="mensajes por segundo")
    p.add_argument("--duration", type=int, default=0, help="segundos (0 = infinito)")
    RobotSim(p.parse_args()).run()


if __name__ == "__main__":
    main()
