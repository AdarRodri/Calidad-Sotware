from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.cita import Cita


def crear_cita(
    paciente_id,
    medico_id,
    fecha_hora,
    motivo=None
):

    cita = Cita(
        paciente_id=paciente_id,
        medico_id=medico_id,
        fecha_hora=fecha_hora,
        motivo=motivo,
        estado="programada"
    )

    try:

        db.session.add(cita)
        db.session.commit()

        return cita, None

    except IntegrityError:

        db.session.rollback()

        return None, "El médico ya tiene una cita en esa fecha y hora"


def obtener_citas(
    paciente_id=None,
    medico_id=None
):
    consulta = Cita.query

    if paciente_id is not None:
        consulta = consulta.filter_by(
            paciente_id=paciente_id
        )

    if medico_id is not None:
        consulta = consulta.filter_by(
            medico_id=medico_id
        )

    return consulta.order_by(
        Cita.fecha_hora.asc()
    ).all()


def obtener_cita_por_id(cita_id):

    return Cita.query.get(cita_id)


def cancelar_cita(cita):

    if cita is None:
        return False

    cita.estado = "cancelada"

    db.session.commit()

    return True