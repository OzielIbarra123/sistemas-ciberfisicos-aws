# ADR 0007: Mantener el control y la seguridad del robot en el sistema local

- **Estado:** Aceptada
- **Fecha:** 2026-10-23

## Contexto
La operación segura no debe depender de la conexión a internet y Lambda no garantiza tiempos deterministas.

## Decisión
El control del movimiento y las funciones de seguridad se ejecutan en el robot; la nube solo supervisa, almacena y alerta. Ante una interrupción, el robot conserva 30 minutos de telemetría y la reenvía al reconectar.

## Alternativas consideradas
Ejecutar el control desde la nube.

## Consecuencias
+ Operación segura ante cortes de internet.
- La nube no puede comandar al robot en tiempo real y la lógica queda repartida entre dos entornos.
