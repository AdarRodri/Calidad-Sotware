import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def ahora():
    """Hora actual de la clínica (sin zona horaria).

    Render ejecuta el servidor en UTC, pero las citas se guardan con la hora local que
    elige el usuario. Por eso se compara siempre contra la hora de la clínica.
    Se puede cambiar con la variable de entorno APP_TIMEZONE (por defecto America/Bogota).
    """
    nombre = os.getenv("APP_TIMEZONE", "America/Bogota")
    try:
        zona = ZoneInfo(nombre)
    except Exception:
        zona = timezone(timedelta(hours=-5))
    return datetime.now(zona).replace(tzinfo=None)
