import re
from datetime import datetime


def validar_email(email):

    if not email:
        return False

    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(
        patron,
        email
    ) is not None


def validar_password(password):

    if not password:
        return False

    return len(password) >= 8


def validar_fecha_hora(fecha_hora):

    if not fecha_hora:
        return False

    try:

        datetime.fromisoformat(
            fecha_hora
        )

        return True

    except ValueError:

        return False