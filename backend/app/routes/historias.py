from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.cita import Cita
from app.models.historia_clinica import HistoriaClinica
from app.models.medico import Medico
from app.utils.decorators import requiere_rol
from app.utils.tiempo import ahora

historias_bp = Blueprint("historias", __name__, url_prefix="/api/historias")

MAX_TEXTO = 4000
NOMBRES_CAMPOS = {
    "diagnostico": "diagnóstico",
    "evolucion": "evolución",
    "observaciones": "observaciones",
}


def medico_actual():
    return Medico.query.filter_by(usuario_id=int(get_jwt_identity())).first()


def leer_texto(data, campo, obligatorio=False):
    nombre = NOMBRES_CAMPOS[campo]
    valor = data.get(campo)
    if valor is None:
        valor = ""
    if not isinstance(valor, str):
        raise ValueError(f"El campo '{nombre}' debe ser texto.")
    valor = valor.strip()
    if obligatorio and not valor:
        raise ValueError(f"El {nombre} es obligatorio.")
    if len(valor) > MAX_TEXTO:
        raise ValueError(f"El campo '{nombre}' no puede superar {MAX_TEXTO} caracteres.")
    return valor or None


def serializar_historia(historia):
    paciente = historia.paciente
    cita = historia.cita
    return {
        "id": historia.id,
        "cita_id": historia.cita_id,
        "paciente_id": historia.paciente_id,
        "paciente_nombre": f"{paciente.nombre} {paciente.apellido}".strip() if paciente else None,
        "medico_id": historia.medico_id,
        "fecha_cita": cita.fecha_hora.isoformat() if cita else None,
        "motivo": cita.motivo if cita else None,
        "diagnostico": historia.diagnostico,
        "evolucion": historia.evolucion,
        "observaciones": historia.observaciones,
        "fecha_registro": historia.fecha_registro.isoformat() if historia.fecha_registro else None,
        "fecha_actualizacion": historia.fecha_actualizacion.isoformat() if historia.fecha_actualizacion else None,
    }


@historias_bp.route("", methods=["GET"])
@requiere_rol("medico")
def listar_historias():
    """Historias clínicas escritas por el médico que inició sesión (opcional: ?paciente_id=)."""
    medico = medico_actual()
    if medico is None:
        return jsonify({"error": "No existe un perfil médico asociado a esta cuenta."}), 404

    consulta = HistoriaClinica.query.filter_by(medico_id=medico.id)
    paciente_id = request.args.get("paciente_id", type=int)
    if paciente_id is not None:
        consulta = consulta.filter_by(paciente_id=paciente_id)

    historias = consulta.all()
    historias.sort(key=lambda h: h.cita.fecha_hora, reverse=True)

    return jsonify({"historias": [serializar_historia(h) for h in historias]}), 200


@historias_bp.route("", methods=["POST"])
@requiere_rol("medico")
def registrar_atencion():
    """Registra la historia clínica de una cita y la marca como atendida."""
    medico = medico_actual()
    if medico is None:
        return jsonify({"error": "No existe un perfil médico asociado a esta cuenta."}), 404

    data = request.get_json(silent=True) or {}

    try:
        cita_id = int(data.get("cita_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Indica la cita que atendiste."}), 400

    try:
        diagnostico = leer_texto(data, "diagnostico", obligatorio=True)
        evolucion = leer_texto(data, "evolucion")
        observaciones = leer_texto(data, "observaciones")
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    cita = Cita.query.get(cita_id)
    if cita is None:
        return jsonify({"error": "Cita no encontrada."}), 404
    if cita.medico_id != medico.id:
        return jsonify({"error": "Solo puedes registrar la atención de tus propias citas."}), 403

    if (cita.estado or "").lower() == "cancelada":
        return jsonify({"error": "No puedes registrar la atención de una cita cancelada."}), 409
    if HistoriaClinica.query.filter_by(cita_id=cita.id).first() is not None:
        return jsonify({"error": "Esta cita ya tiene historia clínica. Edítala desde 'Historias clínicas'."}), 409
    if cita.fecha_hora.date() > ahora().date():
        return jsonify({"error": "Solo puedes registrar la atención desde el día de la cita."}), 409

    historia = HistoriaClinica(
        cita_id=cita.id,
        paciente_id=cita.paciente_id,
        medico_id=medico.id,
        diagnostico=diagnostico,
        evolucion=evolucion,
        observaciones=observaciones,
    )
    cita.estado = "atendida"
    db.session.add(historia)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Esta cita ya tiene historia clínica."}), 409

    return jsonify({
        "mensaje": "La atención se registró y la cita quedó como atendida.",
        "historia": serializar_historia(historia),
    }), 201


@historias_bp.route("/<int:historia_id>", methods=["PUT"])
@requiere_rol("medico")
def actualizar_historia(historia_id):
    """Actualiza el diagnóstico, la evolución o las observaciones de una historia propia."""
    medico = medico_actual()
    if medico is None:
        return jsonify({"error": "No existe un perfil médico asociado a esta cuenta."}), 404

    historia = HistoriaClinica.query.get(historia_id)
    if historia is None:
        return jsonify({"error": "Historia clínica no encontrada."}), 404
    if historia.medico_id != medico.id:
        return jsonify({"error": "Solo puedes editar las historias clínicas que tú registraste."}), 403

    data = request.get_json(silent=True) or {}

    try:
        if "diagnostico" in data:
            historia.diagnostico = leer_texto(data, "diagnostico", obligatorio=True)
        if "evolucion" in data:
            historia.evolucion = leer_texto(data, "evolucion")
        if "observaciones" in data:
            historia.observaciones = leer_texto(data, "observaciones")
    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400

    db.session.commit()
    return jsonify({
        "mensaje": "La historia clínica se actualizó correctamente.",
        "historia": serializar_historia(historia),
    }), 200
