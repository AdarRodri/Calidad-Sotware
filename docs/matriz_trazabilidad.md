# Matriz de Trazabilidad - MediCitas

| Historia | Descripción | Backend (endpoints) | Backend (código) | Frontend | Pruebas |
|---|---|---|---|---|---|
| HU-01 | Registro de paciente | `POST /api/auth/registro` | `routes/auth.py`, `services/auth_service.py` | `js/auth.js`, `js/app.js` | `tests/test_auth.py` |
| HU-02 | Historia clínica | `GET /api/historias`, `POST /api/historias`, `PUT /api/historias/{id}` | `routes/historias.py`, `models/historia_clinica.py` | `js/historias.js`, `js/citas.js` | `tests/test_nuevas_funciones.py` |
| HU-03 | Recordatorios automáticos | `GET /api/notificaciones`, `POST /api/recordatorios/procesar` | `routes/recordatorios.py`, `services/recordatorio_service.py`, `services/email_service.py`, `models/recordatorio.py`, `utils/tiempo.py` | `js/citas.js` (panel del paciente), `js/reportes.js` (botón del administrador) | `tests/test_nuevas_funciones.py` |
| HU-04 | Panel de métricas | `GET /api/reportes/resumen`, `GET /api/reportes/citas.csv` | `routes/reportes.py` | `js/reportes.js` | `tests/test_nuevas_funciones.py` |

La tarea programada que dispara los recordatorios cada hora está en `.github/workflows/recordatorios.yml`.
