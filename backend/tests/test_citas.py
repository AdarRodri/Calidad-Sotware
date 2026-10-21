def test_citas_sin_token(client):

    response = client.get(
        "/api/citas"
    )

    assert response.status_code == 401