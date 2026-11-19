import os
from datetime import timedelta
from html import escape

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.cita import Cita
from app.models.medico import Medico
from app.models.recordatorio import Recordatorio
from app.models.usuario import Usuario
from app.services.email_service import enviar_correo
from app.utils.tiempo import ahora

TIPO = "previo"
ESTADOS_ACTIVOS = ["programada", "confirmada"]


def horas_antes():
    """Con cuántas horas de anticipación se avisa (RECORDATORIO_HORAS, por defecto 24)."""
    try:
        valor = int(os.getenv("RECORDATORIO_HORAS", "24"))
    except ValueError:
        valor = 24
    return min(max(valor, 1), 168)


def construir_mensaje(cita, medico, usuario_medico):
    fecha = cita.fecha_hora
    return (
        f"Recordatorio: tienes una cita con Dr./Dra. {usuario_medico.nombre} "
        f"{usuario_medico.apellido} ({medico.especialidad}) el {fecha:%d/%m/%Y} "
        f"a las {fecha:%I:%M %p}. Si no puedes asistir, cancélala para liberar el horario."
    )


def procesar_recordatorios(paciente_id=None):
    """Crea el recordatorio de cada cita próxima que todavía no lo tiene.

    Revisa las citas programadas o confirmadas que ocurren dentro de las próximas
    `horas_antes()` horas. Es seguro llamarla varias veces: no duplica recordatorios.
    Si se indica `paciente_id`, solo procesa las citas de ese paciente.
    """
    horas = horas_antes()
    inicio = ahora()
    limite = inicio + timedelta(hours=horas)

    consulta = (
        Cita.query
        .filter(Cita.fecha_hora > inicio)
        .filter(Cita.fecha_hora <= limite)
        .filter(Cita.estado.in_(ESTADOS_ACTIVOS))
    )
    if paciente_id is not None:
        consulta = consulta.filter_by(paciente_id=paciente_id)

    citas = consulta.order_by(Cita.fecha_hora.asc()).all()

    resumen = {
        "horas_antes": horas,
        "revisadas": len(citas),
        "creados": 0,
        "correos_enviados": 0,
        "correos_con_error": 0,
    }

    for cita in citas:
        if Recordatorio.query.filter_by(cita_id=cita.id, tipo=TIPO).first() is not None:
            continue

        medico = Medico.query.get(cita.medico_id)
        paciente = Usuario.query.get(cita.paciente_id)
        if medico is None or paciente is None:
            continue

        mensaje = construir_mensaje(cita, medico, medico.usuario)
        recordatorio = Recordatorio(
            cita_id=cita.id,
            paciente_id=paciente.id,
            tipo=TIPO,
            mensaje=mensaje,
        )
        db.session.add(recordatorio)
        try:
            db.session.commit()
        except IntegrityError:  # otro proceso lo creó al mismo tiempo
            db.session.rollback()
            continue

        resumen["creados"] += 1

        html = (
            f"<p>Hola {escape(paciente.nombre)},</p>"
            f"<p>{escape(mensaje)}</p>"
            "<p>Equipo MediCitas</p>"
        )
        estado, _detalle = enviar_correo(
            paciente.email,
            f"{paciente.nombre} {paciente.apellido}",
            "Recordatorio de tu cita médica - MediCitas",
            html,
        )
        recordatorio.estado_correo = estado
        db.session.commit()

        if estado == "enviado":
            resumen["correos_enviados"] += 1
        elif estado == "error":
            resumen["correos_con_error"] += 1

    return resumen
