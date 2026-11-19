import csv
import io
from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, Response

from app.models.cita import Cita
from app.models.medico import Medico
from app.models.recordatorio import Recordatorio
from app.utils.decorators import requiere_rol
from app.utils.tiempo import ahora

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")

ESTADOS_PENDIENTES = ("programada", "confirmada")


def estado_normalizado(cita):
    estado = (cita.estado or "").lower()
    return "programada" if estado == "pendiente" else estado


def leer_fecha(valor, nombre):
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"La fecha '{nombre}' debe tener el formato AAAA-MM-DD.")


def leer_rango():
    desde = leer_fecha(request.args.get("desde"), "desde")
    hasta = leer_fecha(request.args.get("hasta"), "hasta")
    if desde and hasta and desde > hasta:
        raise ValueError("La fecha 'desde' no puede ser posterior a 'hasta'.")
    return desde, hasta


def citas_en_rango(desde, hasta):
    consulta = Cita.query
    if desde:
        consulta = consulta.filter(Cita.fecha_hora >= desde)
    if hasta:
        consulta = consulta.filter(Cita.fecha_hora < hasta + timedelta(days=1))
    return consulta.order_by(Cita.fecha_hora.asc()).all()


def porcentaje(parte, total):
    return round(100 * parte / total, 1) if total else 0.0


@reportes_bp.route("/resumen", methods=["GET"])
@requiere_rol("admin")
def resumen():
    try:
        desde, hasta = leer_rango()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    citas = citas_en_rango(desde, hasta)
    momento = ahora()

    conteo = Counter(estado_normalizado(c) for c in citas)
    total = len(citas)
    pendientes = conteo["programada"] + conteo["confirmada"]
    vencidas = sum(
        1 for c in citas
        if estado_normalizado(c) in ESTADOS_PENDIENTES and c.fecha_hora < momento
    )

    # Por médico (incluye médicos sin citas en el rango).
    filas = {}
    for c in citas:
        fila = filas.setdefault(c.medico_id, {"total": 0, "pendientes": 0, "atendidas": 0, "canceladas": 0})
        fila["total"] += 1
        estado = estado_normalizado(c)
        if estado in ESTADOS_PENDIENTES:
            fila["pendientes"] += 1
        elif estado == "atendida":
            fila["atendidas"] += 1
        elif estado == "cancelada":
            fila["canceladas"] += 1

    por_medico = []
    for medico in Medico.query.all():
        fila = filas.get(medico.id, {"total": 0, "pendientes": 0, "atendidas": 0, "canceladas": 0})
        por_medico.append({
            "medico_id": medico.id,
            "nombre": f"{medico.usuario.nombre} {medico.usuario.apellido}",
            "especialidad": medico.especialidad,
            **fila,
        })
    por_medico.sort(key=lambda m: (-m["total"], m["nombre"]))

    # Por mes (últimos 12 meses con citas).
    meses = {}
    for c in citas:
        clave = c.fecha_hora.strftime("%Y-%m")
        fila = meses.setdefault(clave, {"mes": clave, "total": 0, "pendientes": 0, "atendidas": 0, "canceladas": 0})
        fila["total"] += 1
        estado = estado_normalizado(c)
        if estado in ESTADOS_PENDIENTES:
            fila["pendientes"] += 1
        elif estado == "atendida":
            fila["atendidas"] += 1
        elif estado == "cancelada":
            fila["canceladas"] += 1
    por_mes = [meses[k] for k in sorted(meses)][-12:]

    return jsonify({
        "rango": {
            "desde": desde.date().isoformat() if desde else None,
            "hasta": hasta.date().isoformat() if hasta else None,
        },
        "total": total,
        "por_estado": {
            "programada": conteo["programada"],
            "confirmada": conteo["confirmada"],
            "atendida": conteo["atendida"],
            "cancelada": conteo["cancelada"],
        },
        "pendientes": pendientes,
        "vencidas_sin_atender": vencidas,
        "tasa_atencion": porcentaje(conteo["atendida"], total),
        "tasa_cancelacion": porcentaje(conteo["cancelada"], total),
        "por_medico": por_medico,
        "por_mes": por_mes,
        "recordatorios": {
            "generados": Recordatorio.query.count(),
            "correos_enviados": Recordatorio.query.filter_by(estado_correo="enviado").count(),
        },
    }), 200


def celda_segura(valor):
    """Evita que Excel interprete como fórmula un texto que empieza por = + - @."""
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto[:1] in ("=", "+", "-", "@") else texto


@reportes_bp.route("/citas.csv", methods=["GET"])
@requiere_rol("admin")
def exportar_citas_csv():
    try:
        desde, hasta = leer_rango()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["ID", "Fecha", "Hora", "Paciente", "Médico", "Especialidad", "Estado", "Motivo"])

    for cita in citas_en_rango(desde, hasta):
        paciente = cita.paciente
        medico = cita.medico
        escritor.writerow([
            cita.id,
            cita.fecha_hora.strftime("%Y-%m-%d"),
            cita.fecha_hora.strftime("%H:%M"),
            celda_segura(f"{paciente.nombre} {paciente.apellido}" if paciente else ""),
            celda_segura(f"{medico.usuario.nombre} {medico.usuario.apellido}" if medico else ""),
            celda_segura(medico.especialidad if medico else ""),
            estado_normalizado(cita),
            celda_segura(cita.motivo),
        ])

    return Response(
        "\ufeff" + salida.getvalue(),  # BOM para que Excel respete las tildes
        content_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=reporte_citas.csv"},
    )
