# ADR 0006: Autenticar a los usuarios del dashboard con Amazon Cognito

- **Estado:** Aceptada
- **Fecha:** 2026-10-23

## Contexto
Operadores, supervisores, personal de mantenimiento y administradores necesitan iniciar sesión y ver solo lo que su rol permite.

## Decisión
Utilizar Cognito para la autenticación; API Gateway valida el token y el backend comprueba rol y almacenes permitidos.

## Alternativas consideradas
Usuarios IAM; autenticación propia.

## Consecuencias
+ Autenticación administrada y separación entre identidades de personas y de recursos.
- Requiere configurar grupos y roles, y crea una dependencia del servicio. (Pendiente de incluir en la plantilla.)
