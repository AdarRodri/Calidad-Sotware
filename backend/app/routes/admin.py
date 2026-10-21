import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash

from app.models.medico import Medico
from app.models.usuario import Usuario  # Ajusta si tu modelo se llama distinto.

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TELEFONO_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def asignar_password(usuario, password):
    """Guarda la contraseña cifrada según cómo esté definido tu modelo Usuario."""
    if hasattr(usuario, "set_password"):
        usuario.set_password(password)
    elif hasattr(Usuario, "password_hash"):
        usuario.password_hash = generate_password_hash(password)
    elif hasattr(Usuario, "password"):
        usuario.password = generate_password_hash(password)
    else:
        raise RuntimeError("No se encontró el campo de contraseña en el modelo Usuario.")


def asignar_si_existe(objeto, campo, valor):
    if hasattr(type(objeto), campo):
        setattr(objeto, campo, valor)
        return True
    return False


@admin_bp.route("/medicos", methods=["POST"])
@jwt_required()
def registrar_medico():
    if get_jwt().get("rol") != "admin":
        return jsonify({"error": "Solo un administrador puede registrar médicos."}), 403

    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    especialidad = (data.get("especialidad") or "").strip()
    telefono = (data.get("telefono") or "").strip()

    if not all([nombre, apellido, email, password, especialidad]):
        return jsonify({"error": "Completa nombre, apellido, correo, contraseña y especialidad."}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "El correo electrónico no es válido."}), 400
    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres."}), 400
    if telefono and not TELEFONO_RE.match(telefono):
        return jsonify({"error": "El teléfono no es válido. Usa solo números, espacios, + o guiones."}), 400

    if Usuario.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Ya existe una cuenta con ese correo electrónico."}), 409

    sesion = Usuario.query.session
    try:
        usuario = Usuario(nombre=nombre, apellido=apellido, email=email, rol="medico")
        asignar_password(usuario, password)
        sesion.add(usuario)
        sesion.flush()  # Genera usuario.id sin cerrar la transacción.

        medico = Medico(usuario_id=usuario.id, especialidad=especialidad)
        # Algunos proyectos guardan estos datos también en la tabla de médicos.
        asignar_si_existe(medico, "nombre", nombre)
        asignar_si_existe(medico, "apellido", apellido)
        if telefono:
            if not asignar_si_existe(medico, "telefono", telefono):
                asignar_si_existe(usuario, "telefono", telefono)
        sesion.add(medico)
        sesion.commit()
    except Exception as error:
        sesion.rollback()
        return jsonify({"error": f"No se pudo registrar al médico: {error}"}), 500

    return jsonify({
        "mensaje": f"El médico {nombre} {apellido} se registró correctamente.",
        "medico": {
            "id": medico.id,
            "usuario_id": usuario.id,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "especialidad": especialidad,
            "telefono": telefono or None,
        },
    }), 201
