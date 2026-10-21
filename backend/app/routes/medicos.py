from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required

from app.extensions import db

from app.models.usuario import Usuario
from app.models.medico import Medico

from app.utils.decorators import requiere_rol


medicos_bp = Blueprint(
    "medicos",
    __name__,
    url_prefix="/api/medicos"
)


@medicos_bp.route(
    "",
    methods=["GET"]
)
@jwt_required()
def listar_medicos():

    medicos = Medico.query.all()

    resultado = []

    for medico in medicos:

        resultado.append({

            "id": medico.id,

            "usuario_id": medico.usuario_id,

            "nombre": medico.usuario.nombre,

            "apellido": medico.usuario.apellido,

            "email": medico.usuario.email,

            "especialidad": medico.especialidad,

            "telefono": medico.telefono

        })

    return jsonify({
        "medicos": resultado
    }), 200


@medicos_bp.route(
    "/<int:medico_id>",
    methods=["GET"]
)
@jwt_required()
def obtener_medico(medico_id):

    medico = Medico.query.get(
        medico_id
    )

    if medico is None:

        return jsonify({
            "error": "Médico no encontrado"
        }), 404

    return jsonify({

        "id": medico.id,

        "usuario_id": medico.usuario_id,

        "nombre": medico.usuario.nombre,

        "apellido": medico.usuario.apellido,

        "email": medico.usuario.email,

        "especialidad": medico.especialidad,

        "telefono": medico.telefono

    }), 200


@medicos_bp.route(
    "",
    methods=["POST"]
)
@requiere_rol("admin")
def crear_medico():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "El cuerpo es obligatorio"
        }), 400

    campos = [
        "nombre",
        "apellido",
        "email",
        "password",
        "especialidad"
    ]

    for campo in campos:

        if not data.get(campo):

            return jsonify({
                "error": (
                    f"El campo '{campo}' "
                    "es obligatorio"
                )
            }), 400

    email = data["email"].strip().lower()

    usuario_existente = Usuario.query.filter_by(
        email=email
    ).first()

    if usuario_existente:

        return jsonify({
            "error": (
                "El correo electrónico "
                "ya está registrado"
            )
        }), 409

    from app.extensions import bcrypt

    password_hash = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    usuario = Usuario(

        nombre=data["nombre"].strip(),

        apellido=data["apellido"].strip(),

        email=email,

        password_hash=password_hash,

        rol="medico"

    )

    db.session.add(usuario)

    db.session.flush()

    medico = Medico(

        usuario_id=usuario.id,

        especialidad=data["especialidad"].strip(),

        telefono=data.get("telefono")

    )

    db.session.add(medico)

    db.session.commit()

    return jsonify({

        "mensaje": "Médico creado correctamente",

        "medico": {

            "id": medico.id,

            "usuario_id": usuario.id,

            "nombre": usuario.nombre,

            "apellido": usuario.apellido,

            "email": usuario.email,

            "especialidad": medico.especialidad,

            "telefono": medico.telefono

        }

    }), 201


@medicos_bp.route(
    "/<int:medico_id>",
    methods=["PUT"]
)
@requiere_rol("admin")
def actualizar_medico(medico_id):

    medico = Medico.query.get(
        medico_id
    )

    if medico is None:

        return jsonify({
            "error": "Médico no encontrado"
        }), 404

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "El cuerpo es obligatorio"
        }), 400

    if data.get("especialidad"):

        medico.especialidad = (
            data["especialidad"].strip()
        )

    if "telefono" in data:

        medico.telefono = data["telefono"]

    if data.get("nombre"):

        medico.usuario.nombre = (
            data["nombre"].strip()
        )

    if data.get("apellido"):

        medico.usuario.apellido = (
            data["apellido"].strip()
        )

    db.session.commit()

    return jsonify({

        "mensaje": "Médico actualizado correctamente"

    }), 200


@medicos_bp.route(
    "/<int:medico_id>",
    methods=["DELETE"]
)
@requiere_rol("admin")
def eliminar_medico(medico_id):

    medico = Medico.query.get(
        medico_id
    )

    if medico is None:

        return jsonify({
            "error": "Médico no encontrado"
        }), 404

    usuario = medico.usuario

    db.session.delete(medico)

    db.session.delete(usuario)

    db.session.commit()

    return jsonify({

        "mensaje": "Médico eliminado correctamente"

    }), 200