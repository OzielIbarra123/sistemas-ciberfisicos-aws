# Infraestructura como código (IaC)

La infraestructura se define con **AWS CloudFormation** en `cloudformation/telemetry-stack.yaml`. Los scripts de `scripts/` validan, empaquetan el código de las Lambdas (`src/lambdas/`) y despliegan la pila.

## Recursos que crea la pila

| Recurso | Función |
|---|---|
| S3 (`RawBucket`) | Capa Bronze: mensajes originales en `telemetria/maquinas/<dispositivo>/<fecha>/`. Cifrado, acceso público bloqueado, solo TLS, ciclo de vida a IA (30 días) y Glacier (180 días). |
| DynamoDB (`TelemetryTable`) | Capa Silver. Partition key `device_id`; sort key `sk` = `<ts>#<event_id>` (historial idempotente) o `LATEST` (último estado). Bajo demanda y con recuperación a un punto en el tiempo. |
| IoT Core (`TelemetryRule`) | Regla `SELECT * FROM 'almacen/robots/+/telemetria'` que invoca la Lambda de procesamiento. |
| Lambda (`ProcessorFunction`) | Guarda en S3 y DynamoDB, evita duplicados y publica alertas. |
| Lambda (`SupervisorFunction`) + EventBridge | Cada minuto detecta dispositivos con más de 60 s sin datos. |
| SNS | Alertas por correo. |
| IAM | Un rol por función con permisos mínimos; permisos de invocación restringidos por cuenta y ARN. |
| CloudWatch | Grupos de logs con retención de 30 días y alarma de errores de procesamiento. |

No se usa VPC ni Security Groups en esta versión (ver ADR 0005).

## Requisitos

- Cuenta de AWS y **AWS CLI v2** configurada (`aws configure`).
- Región por defecto: `us-east-2` (Ohio).

## Despliegue

```powershell
cd infrastructure\scripts
.\deploy.ps1 -AlertEmail tu_correo@ejemplo.com
```

```bash
./deploy.sh tu_correo@ejemplo.com us-east-2 sci-almacen
```

El script crea un bucket de artefactos (`<pila>-artifacts-<cuenta>`), ejecuta `aws cloudformation package` y `deploy`, y muestra las salidas (bucket, tabla, tema SNS). Confirma la suscripción de SNS desde tu correo.

## Dar de alta un dispositivo

1. IoT Core → *Manage → All devices → Things → Create thing* (`robot-01`), con certificado nuevo.
2. Descargar certificado, llave privada y `AmazonRootCA1.pem` (guardarlos fuera del repositorio).
3. Adjuntar al certificado una política que permita únicamente `iot:Connect` con su client id y publicar/suscribirse en `almacen/robots/robot-01/*`.
4. Ejecutar `src/device_sim_TX_RX.py` con esos archivos.

## Eliminación

```powershell
.\destroy.ps1
```

Vacía el bucket (incluidas versiones) y borra la pila.
