from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from sqlalchemy.orm import object_session

from app.models.cita import Cita
from app.models.medico import Medico

try:
    from app.models.usuario import Usuario
except ImportError:  # Si tu modelo se llama distinto, ajusta esta línea.
    Usuario = None
from app.services.cita_service import (
    crear_cita,
    obtener_citas,
    obtener_cita_por_id,
    cancelar_cita,
)

citas_bp = Blueprint("citas", __name__, url_prefix="/api/citas")


def nombre_paciente(paciente_id):
    """Devuelve 'Nombre Apellido' del paciente o None si no se puede resolver."""
    if Usuario is None:
        return None
    usuario = Usuario.query.get(paciente_id)
    if usuario is None:
        return None
    return f"{getattr(usuario, 'nombre', '')} {getattr(usuario, 'apellido', '')}".strip() or None


def serializar_cita(cita):
    return {
        "id": cita.id,
        "paciente_id": cita.paciente_id,
        "paciente_nombre": nombre_paciente(cita.paciente_id),
        "medico_id": cita.medico_id,
        "fecha_hora": cita.fecha_hora.isoformat(),
        "motivo": cita.motivo,
        "estado": cita.estado,
        "fecha_creacion": cita.fecha_creacion.isoformat() if cita.fecha_creacion else None,
    }


def usuario_puede_ver_cita(cita, usuario_id, rol):
    if rol == "admin":
        return True
    if rol == "paciente":
        return cita.paciente_id == usuario_id
    if rol == "medico":
        medico = Medico.query.filter_by(usuario_id=usuario_id).first()
        return medico is not None and cita.medico_id == medico.id
    return False


@citas_bp.route("", methods=["GET"])
@jwt_required()
def listar_citas():
    usuario_id = int(get_jwt_identity())
    rol = get_jwt().get("rol")

    if rol == "paciente":
        citas = obtener_citas(paciente_id=usuario_id)
    elif rol == "medico":
        medico = Medico.query.filter_by(usuario_id=usuario_id).first()
        if medico is None:
            return jsonify({"error": "No existe un perfil médico asociado a esta cuenta."}), 404
        citas = obtener_citas(medico_id=medico.id)
    elif rol == "admin":
        citas = obtener_citas()
    else:
        return jsonify({"error": "Rol de usuario no autorizado."}), 403

    return jsonify({"citas": [serializar_cita(cita) for cita in citas]}), 200


@citas_bp.route("", methods=["POST"])
@jwt_required()
def crear():
    rol = get_jwt().get("rol")
    if rol != "paciente":
        return jsonify({"error": "Solo una cuenta de paciente puede solicitar una cita."}), 403

    data = request.get_json(silent=True) or {}
    medico_id = data.get("medico_id")
    fecha_hora = data.get("fecha_hora")
    motivo = (data.get("motivo") or "").strip()

    if not medico_id or not fecha_hora:
        return jsonify({"error": "Selecciona un médico y una fecha y hora."}), 400

    try:
        medico_id = int(medico_id)
    except (TypeError, ValueError):
        return jsonify({"error": "El médico seleccionado no es válido."}), 400

    medico = Medico.query.get(medico_id)
    if medico is None:
        return jsonify({"error": "El médico seleccionado no existe."}), 404

    try:
        fecha = datetime.fromisoformat(fecha_hora)
    except (TypeError, ValueError):
        return jsonify({"error": "La fecha debe tener un formato válido."}), 400

    if fecha <= datetime.now():
        return jsonify({"error": "La cita debe programarse para una fecha y hora futuras."}), 400

    paciente_id = int(get_jwt_identity())
    cita, error = crear_cita(
        paciente_id=paciente_id,
        medico_id=medico.id,
        fecha_hora=fecha,
        motivo=motivo[:500] or None,
    )
    if error:
        return jsonify({"error": error}), 409

    return jsonify({
        "mensaje": "Tu cita se registró correctamente.",
        "cita": serializar_cita(cita),
    }), 201


@citas_bp.route("/<int:cita_id>", methods=["GET"])
@jwt_required()
def obtener(cita_id):
    cita = obtener_cita_por_id(cita_id)
    if cita is None:
        return jsonify({"error": "Cita no encontrada."}), 404

    usuario_id = int(get_jwt_identity())
    rol = get_jwt().get("rol")
    if not usuario_puede_ver_cita(cita, usuario_id, rol):
        return jsonify({"error": "No tienes permiso para consultar esta cita."}), 403

    return jsonify(serializar_cita(cita)), 200


@citas_bp.route("/<int:cita_id>/cancelar", methods=["PUT"])
@jwt_required()
def cancelar(cita_id):
    cita = obtener_cita_por_id(cita_id)
    if cita is None:
        return jsonify({"error": "Cita no encontrada."}), 404

    usuario_id = int(get_jwt_identity())
    rol = get_jwt().get("rol")
    if rol != "paciente" or cita.paciente_id != usuario_id:
        return jsonify({"error": "Solo puedes cancelar tus propias citas."}), 403

    if cita.estado == "cancelada":
        return jsonify({"error": "Esta cita ya está cancelada."}), 409
    if cita.estado == "atendida":
        return jsonify({"error": "No puedes cancelar una cita que ya fue atendida."}), 409
    if cita.fecha_hora <= datetime.now():
        return jsonify({"error": "No puedes cancelar una cita cuya hora ya pasó."}), 409

    cancelar_cita(cita)
    return jsonify({"mensaje": "La cita se canceló correctamente."}), 200


@citas_bp.route("/<int:cita_id>/confirmar", methods=["PUT"])
@jwt_required()
def confirmar(cita_id):
    cita = obtener_cita_por_id(cita_id)
    if cita is None:
        return jsonify({"error": "Cita no encontrada."}), 404

    usuario_id = int(get_jwt_identity())
    rol = get_jwt().get("rol")
    if rol != "medico":
        return jsonify({"error": "Solo un médico puede confirmar citas."}), 403

    medico = Medico.query.filter_by(usuario_id=usuario_id).first()
    if medico is None or cita.medico_id != medico.id:
        return jsonify({"error": "Solo puedes confirmar las citas dirigidas a ti."}), 403

    estado = (cita.estado or "").lower()
    if estado == "confirmada":
        return jsonify({"error": "Esta cita ya está confirmada."}), 409
    if estado == "cancelada":
        return jsonify({"error": "No puedes confirmar una cita cancelada."}), 409
    if estado == "atendida":
        return jsonify({"error": "Esta cita ya fue atendida."}), 409
    if cita.fecha_hora <= datetime.now():
        return jsonify({"error": "No puedes confirmar una cita cuya hora ya pasó."}), 409

    cita.estado = "confirmada"
    object_session(cita).commit()
    return jsonify({
        "mensaje": "La cita se confirmó correctamente.",
        "cita": serializar_cita(cita),
    }), 200
