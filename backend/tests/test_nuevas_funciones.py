"""Pruebas de seguridad de historias clínicas, recordatorios y reportes.

Verifican que ninguno de los endpoints nuevos responde sin iniciar sesión.
"""


def test_historias_sin_token(client):
    assert client.get("/api/historias").status_code == 401


def test_registrar_atencion_sin_token(client):
    response = client.post("/api/historias", json={"cita_id": 1, "diagnostico": "x"})
    assert response.status_code == 401


def test_actualizar_historia_sin_token(client):
    response = client.put("/api/historias/1", json={"diagnostico": "x"})
    assert response.status_code == 401


def test_notificaciones_sin_token(client):
    assert client.get("/api/notificaciones").status_code == 401


def test_procesar_recordatorios_sin_token(client):
    assert client.post("/api/recordatorios/procesar").status_code == 401


def test_resumen_reportes_sin_token(client):
    assert client.get("/api/reportes/resumen").status_code == 401


def test_exportar_csv_sin_token(client):
    assert client.get("/api/reportes/citas.csv").status_code == 401
