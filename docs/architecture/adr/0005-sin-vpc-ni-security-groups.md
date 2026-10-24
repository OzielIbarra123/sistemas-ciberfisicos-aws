# ADR 0005: No conectar las Lambdas a una VPC en esta versión

- **Estado:** Aceptada
- **Fecha:** 2026-10-23

## Contexto
Las funciones usan únicamente servicios administrados (IoT Core, S3, DynamoDB, SNS) y no acceden a servidores ni bases de datos en subredes privadas.

## Decisión
No asignar VPC ni Security Groups. El acceso se protege con IAM de mínimo privilegio, políticas de recursos, TLS y bloqueo de acceso público en S3.

## Alternativas consideradas
Lambda dentro de una VPC con subredes privadas.

## Consecuencias
+ Menor complejidad y sin costos de red adicionales.
- No hay segmentación de red. Si se incorpora Aurora o un servidor EC2 privado, se deberá usar una VPC y Security Groups que permitan solo las conexiones necesarias.
