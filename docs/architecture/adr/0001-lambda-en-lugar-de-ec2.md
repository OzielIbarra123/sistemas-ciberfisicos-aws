# ADR 0001: Usar AWS Lambda en lugar de EC2 para el procesamiento

- **Estado:** Aceptada
- **Fecha:** 2026-10-23

## Contexto
Los mensajes de telemetría son pequeños y llegan por eventos (≈25.9 millones al mes con 10 dispositivos a 1 mensaje/s). Las consultas y la supervisión también son tareas breves. Ninguna requiere un servidor permanentemente activo.

## Decisión
Utilizar AWS Lambda para validar la telemetría, atender las consultas del dashboard y supervisar dispositivos.

## Alternativas consideradas
Amazon EC2; contenedores con ECS y Fargate.

## Consecuencias
+ Sin administración de servidores ni parches; escalamiento automático; se paga por ejecución.
- Menor control del entorno de ejecución; límite de 15 minutos por ejecución; posibles arranques en frío; no apta para control con tiempos estrictamente deterministas (por eso el control del robot se mantiene local, ADR 0007).
