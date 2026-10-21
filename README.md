# MediCitas

Sistema web para la gestión de citas médicas.

## Tecnologías

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Flask-JWT-Extended
- Flask-Bcrypt

### Frontend

- HTML5
- CSS3
- JavaScript ES6

## Arquitectura

El proyecto utiliza una arquitectura por capas:

- Models
- Routes
- Services
- Utils

## Seguridad

El sistema implementa:

- JWT
- bcrypt
- RBAC
- Validación de datos
- Control de acceso
- No almacenamiento de credenciales en frontend

## Base de datos

PostgreSQL.

Principales tablas:

- usuarios
- medicos
- citas

La tabla citas contiene una restricción única:

`UNIQUE(medico_id, fecha_hora)`

para impedir la doble reserva de un médico.

## Ejecución

Entrar al backend:

```bash
cd backend