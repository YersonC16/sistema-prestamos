# Referencia de API

Documentación interactiva (Swagger):

- asset-service: http://localhost:8001/docs
- loan-service: http://localhost:8002/docs

Los endpoints protegidos requieren `Authorization: Bearer <token>`.

## asset-service (8001)

| Método | Ruta              | Descripción                   | Rol requerido              |
| ------ | ----------------- | ----------------------------- | -------------------------- |
| POST   | /auth/login       | Iniciar sesión (devuelve JWT) | Público                    |
| POST   | /auth/register    | Crear usuario                 | Administrador              |
| GET    | /auth/me          | Usuario autenticado           | Cualquiera autenticado     |
| POST   | /assets/          | Registrar activo              | Administrador, Almacenista |
| GET    | /assets/          | Listar activos                | Cualquiera autenticado     |
| GET    | /assets/available | Listar activos disponibles    | Cualquiera autenticado     |
| GET    | /health           | Estado del servicio           | Público                    |

## loan-service (8002)

| Método | Ruta               | Descripción          | Rol requerido          |
| ------ | ------------------ | -------------------- | ---------------------- |
| POST   | /loans/            | Crear préstamo       | Cualquiera autenticado |
| GET    | /loans/            | Listar préstamos     | Cualquiera autenticado |
| PUT    | /loans/{id}/return | Registrar devolución | Cualquiera autenticado |
| GET    | /health            | Estado del servicio  | Público                |

## Códigos frecuentes

| Código | Significado                                    |
| ------ | ---------------------------------------------- |
| 400    | Datos inválidos o activo no disponible         |
| 401    | Sin token o token inválido                     |
| 403    | Rol sin permiso                                |
| 404    | Recurso no encontrado                          |
| 502    | loan-service no pudo consultar a asset-service |
