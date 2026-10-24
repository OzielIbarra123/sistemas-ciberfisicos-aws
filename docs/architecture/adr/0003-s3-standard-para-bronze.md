# ADR 0003: Guardar los mensajes originales en S3 Standard (capa Bronze)

- **Estado:** Aceptada
- **Fecha:** 2026-10-23

## Contexto
Los datos recientes deben estar disponibles de inmediato para revisión y reprocesamiento; los antiguos se consultan poco.

## Decisión
Utilizar S3 Standard con una política de ciclo de vida: Standard-IA a los 30 días y Glacier a los 180.

## Alternativas consideradas
Clases de archivo (Glacier) desde el inicio; Standard-IA.

## Consecuencias
+ Disponibilidad inmediata y simplicidad; el costo baja con el tiempo gracias al ciclo de vida.
- Costo por GB mayor que el de una clase de archivo durante el primer mes.
