# ADR 0002: Usar DynamoDB en lugar de Aurora para la capa Silver

- **Estado:** Aceptada
- **Fecha:** 2026-10-23

## Contexto
Los datos llegan como JSON y las consultas principales son por dispositivo y periodo. No hay relaciones complejas ni consultas SQL con múltiples tablas.

## Decisión
Utilizar Amazon DynamoDB bajo demanda. Partition key `device_id`; sort key `sk` (`<ts>#<event_id>` o `LATEST`).

## Alternativas consideradas
Amazon Aurora.

## Consecuencias
+ Escala sin administrar instancias, cobro por uso y modelo de documentos acorde al JSON.
- Se pierde la flexibilidad de SQL y los joins; los patrones de acceso deben definirse desde el diseño de claves.
