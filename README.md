# Sistemas Ciberfísicos — Cómputo en la nube con AWS

Repositorio del módulo de cómputo en la nube (Tecnológico de Monterrey, 7.º semestre, bloque Sistemas Ciberfísicos). Aquí se versiona y aloja el código del sistema en la nube, la infraestructura como código (IaC), la documentación y los diagramas.

## Caso de uso

Supervisión IoT de robots móviles y sensores de un almacén inteligente: los dispositivos publican telemetría por MQTT, la nube la almacena por capas (Bronze/Silver), genera alertas y detecta equipos que dejaron de reportar. El control del movimiento y las funciones de seguridad del robot permanecen en el sistema local.

## Arquitectura (resumen)

```
Robots/sensores ─MQTT+TLS→ AWS IoT Core ─regla→ Lambda (procesar) ─┬→ S3 Standard   (Bronze: mensaje original)
                                                                   ├→ DynamoDB      (Silver: historial y último estado)
                                                                   └→ SNS           (alertas)
EventBridge (cada 1 min) → Lambda (supervisar) → DynamoDB / SNS
CloudWatch (logs, métricas, alarma) · IAM (un rol de mínimo privilegio por función)
```

Detalle y diagrama en [`docs/architecture/overview.md`](docs/architecture/overview.md). Decisiones técnicas en [`docs/architecture/adr/`](docs/architecture/adr/).

## Estructura

```
sistemas-ciberfisicos-aws/
├── README.md
├── infrastructure/
│   ├── README.md                      ← cómo desplegar y eliminar la pila
│   ├── cloudformation/
│   │   └── telemetry-stack.yaml       ← IaC: IoT Core, Lambda, S3, DynamoDB, SNS, IAM, CloudWatch
│   └── scripts/                       ← deploy.ps1 / destroy.ps1 (Windows) y deploy.sh (bash)
├── src/
│   ├── device_sim_TX_RX.py            ← simulador de robot (TX telemetría / RX comandos)
│   ├── requirements.txt
│   └── lambdas/
│       ├── process_telemetry.py       ← Bronze + Silver + alertas
│       └── supervise_devices.py       ← detección de equipos sin datos
└── docs/
    └── architecture/
        ├── overview.md
        ├── diagrams/                  ← diagrama (PNG) y fuente editable (PPTX)
        └── adr/                       ← Architecture Decision Records
```

## Inicio rápido

```bash
# 1. Desplegar la infraestructura (requiere AWS CLI configurada)
cd infrastructure/scripts
./deploy.sh tu_correo@ejemplo.com            # Linux/macOS
.\deploy.ps1 -AlertEmail tu_correo@ejemplo.com   # Windows (PowerShell)

# 2. Simular un robot (requiere un "thing" y certificados en AWS IoT Core)
pip install -r src/requirements.txt
python src/device_sim_TX_RX.py --endpoint <prefijo>-ats.iot.us-east-2.amazonaws.com \
    --cert robot-01.cert.pem --key robot-01.private.key --ca AmazonRootCA1.pem \
    --device-id robot-01 --duration 60
```

Los certificados (`*.pem`, `*.key`) **nunca** se suben al repositorio (ver `.gitignore`).

## Costos

La solución es serverless y de pago por uso. Para evitar cargos: eliminar la pila con `destroy` al terminar, mantener la retención de logs en 30 días y configurar alertas en AWS Budgets.

## Equipo

- Oziel Ibarra Martínez
- Luis Antonio Canales Mayo
- Bruno Guzmán García
- Ari Benett Zedillo López

