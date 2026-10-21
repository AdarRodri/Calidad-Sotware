def test_medicos_sin_token(client):

    response = client.get(
        "/api/medicos"
    )

    assert response.status_code == 401