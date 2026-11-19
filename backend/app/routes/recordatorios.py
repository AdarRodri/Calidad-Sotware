import hmac
import os

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from app.extensions import db
from app.models.recordatorio import Recordatorio
from app.services.recordatorio_service import procesar_recordatorios, ESTADOS_ACTIVOS
from app.utils.decorators import requiere_rol
from app.utils.tiempo import ahora

recordatorios_bp = Blueprint("recordatorios", __name__, url_prefix="/api")


def serializar_notificacion(recordatorio):
    return {
        "id": recordatorio.id,
        "cita_id": recordatorio.cita_id,
        "mensaje": recordatorio.mensaje,
        "fecha_cita": recordatorio.cita.fecha_hora.isoformat(),
        "fecha_creacion": recordatorio.fecha_creacion.isoformat() if recordatorio.fecha_creacion else None,
        "correo": recordatorio.estado_correo,
    }


@recordatorios_bp.route("/notificaciones", methods=["GET"])
@requiere_rol("paciente")
def listar_notificaciones():
    """Recordatorios vigentes del paciente. Al consultarlos también se generan los pendientes."""
    paciente_id = int(get_jwt_identity())

    try:
        procesar_recordatorios(paciente_id=paciente_id)
    except Exception:
        db.session.rollback()
        current_app.logger.exception("No se pudieron generar los recordatorios")

    recordatorios = (
        Recordatorio.query
        .filter_by(paciente_id=paciente_id)
        .order_by(Recordatorio.fecha_creacion.desc())
        .all()
    )

    momento = ahora()
    vigentes = [
        r for r in recordatorios
        if r.cita is not None
        and r.cita.fecha_hora > momento
        and (r.cita.estado or "").lower() in ESTADOS_ACTIVOS
    ]
    vigentes.sort(key=lambda r: r.cita.fecha_hora)

    return jsonify({"notificaciones": [serializar_notificacion(r) for r in vigentes]}), 200


@recordatorios_bp.route("/recordatorios/procesar", methods=["POST"])
def ejecutar_recordatorios():
    """Genera (y envía) los recordatorios de las citas próximas.

    Lo puede llamar:
      - una tarea programada, enviando la cabecera X-Cron-Token (variable CRON_TOKEN), o
      - un administrador con sesión iniciada (botón del panel de métricas).
    """
    esperado = os.getenv("CRON_TOKEN")
    recibido = request.headers.get("X-Cron-Token")
    autorizado = bool(esperado and recibido and hmac.compare_digest(recibido, esperado))

    if not autorizado:
        verify_jwt_in_request()
        if get_jwt().get("rol") != "admin":
            return jsonify({"error": "No tienes permisos para realizar esta operación"}), 403

    resumen = procesar_recordatorios()
    return jsonify({
        "mensaje": f"Se crearon {resumen['creados']} recordatorio(s) nuevo(s).",
        "resumen": resumen,
    }), 200
