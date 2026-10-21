def test_registro_cliente(client):

    response = client.post(
        "/api/auth/registro",
        json={
            "nombre": "Test",
            "apellido": "Usuario",
            "email": "test@medicitas.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 201


def test_login_incorrecto(client):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "noexiste@medicitas.com",
            "password": "incorrecta"
        }
    )

    assert response.status_code == 401