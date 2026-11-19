from locust import HttpUser, between, task


class MediCitasUsuario(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        # Ajusta la ruta y payload según app/routes/auth.py
        resp = self.client.post(
            "/api/auth/login",
            json={
                "email": "usuario@ejemplo.com",
                "password": "TuPassword123",
            },
            name="/api/auth/login",
        )
        if resp.status_code == 200:
            data = resp.json()
            self.token = data.get("access_token") or data.get("token")

    def _headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(2)
    def consultar_medicos(self):
        self.client.get(
            "/api/medicos",
            headers=self._headers(),
            name="/api/medicos",
        )

    @task(1)
    def consultar_citas(self):
        self.client.get(
            "/api/citas",
            headers=self._headers(),
            name="/api/citas",
        )
