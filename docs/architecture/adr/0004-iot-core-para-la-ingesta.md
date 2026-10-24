# ADR 0004: Recibir la telemetría con AWS IoT Core

- **Estado:** Aceptada
- **Fecha:** 2026-10-23

## Contexto
Los robots publican por MQTT y cada uno necesita una identidad propia.

## Decisión
Utilizar AWS IoT Core con certificado y política por dispositivo, y una regla que invoca la Lambda de procesamiento.

## Alternativas consideradas
Servidor MQTT propio (p. ej. Mosquitto) en EC2; envío por HTTP a API Gateway.

## Consecuencias
+ Identidad por dispositivo, políticas por tópico y reglas integradas, sin operar un broker.
- Mayor dependencia de AWS y costo proporcional al número de mensajes.
