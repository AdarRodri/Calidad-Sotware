"""Envío de correos por API web (HTTPS).

Render bloquea el correo SMTP (puertos 25, 465 y 587) en el plan gratuito, por eso se usa
la API de Brevo. Es OPCIONAL: si no están definidas las variables, los recordatorios se
generan igual dentro de la aplicación y solo se omite el correo.

Variables de entorno:
    BREVO_API_KEY            clave de la API de Brevo
    EMAIL_REMITENTE          correo remitente (verificado en Brevo)
    EMAIL_NOMBRE_REMITENTE   nombre que verá el paciente (opcional, por defecto "MediCitas")
"""
import json
import os
import urllib.error
import urllib.request

URL_BREVO = "https://api.brevo.com/v3/smtp/email"


def correo_configurado():
    return bool(os.getenv("BREVO_API_KEY") and os.getenv("EMAIL_REMITENTE"))


def enviar_correo(destinatario, nombre, asunto, html):
    """Devuelve (estado, detalle). estado: 'enviado', 'error' o 'no_configurado'."""
    if not correo_configurado():
        return "no_configurado", None

    cuerpo = {
        "sender": {
            "name": os.getenv("EMAIL_NOMBRE_REMITENTE", "MediCitas"),
            "email": os.getenv("EMAIL_REMITENTE"),
        },
        "to": [{"email": destinatario, "name": nombre}],
        "subject": asunto,
        "htmlContent": html,
    }

    peticion = urllib.request.Request(
        URL_BREVO,
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={
            "api-key": os.getenv("BREVO_API_KEY"),
            "content-type": "application/json",
            "accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(peticion, timeout=10):
            return "enviado", None
    except urllib.error.HTTPError as error:
        return "error", f"HTTP {error.code}"
    except Exception as error:  # red caída, tiempo agotado, etc.
        return "error", type(error).__name__
