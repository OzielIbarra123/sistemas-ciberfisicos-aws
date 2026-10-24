# Architecture Decision Records (ADR)

Cada ADR documenta una decisión técnica: contexto, decisión, alternativas y consecuencias (trade-offs).

| # | Decisión | Estado |
|---|---|---|
| 0001 | [Usar AWS Lambda en lugar de EC2 para el procesamiento](0001-lambda-en-lugar-de-ec2.md) | Aceptada |
| 0002 | [Usar DynamoDB en lugar de Aurora para la capa Silver](0002-dynamodb-en-lugar-de-aurora.md) | Aceptada |
| 0003 | [Guardar los mensajes originales en S3 Standard (capa Bronze)](0003-s3-standard-para-bronze.md) | Aceptada |
| 0004 | [Recibir la telemetría con AWS IoT Core](0004-iot-core-para-la-ingesta.md) | Aceptada |
| 0005 | [No conectar las Lambdas a una VPC en esta versión](0005-sin-vpc-ni-security-groups.md) | Aceptada |
| 0006 | [Autenticar a los usuarios del dashboard con Amazon Cognito](0006-cognito-para-usuarios-del-dashboard.md) | Aceptada |
| 0007 | [Mantener el control y la seguridad del robot en el sistema local](0007-control-local-del-robot.md) | Aceptada |

## Plantilla

```markdown
# ADR NNNN: Título

- **Estado:** Propuesta | Aceptada | Reemplazada
- **Fecha:** AAAA-MM-DD

## Contexto
## Decisión
## Alternativas consideradas
## Consecuencias
```
