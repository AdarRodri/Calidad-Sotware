from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from app.services.auth_service import (
    registrar_usuario,
    autenticar_usuario
)

from app.models.usuario import Usuario

from app.utils.decorators import requiere_rol

from app.utils.validators import (
    validar_email,
    validar_password
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route(
    "/registro",
    methods=["POST"]
)
def registro():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": (
                "El cuerpo de la solicitud "
                "es obligatorio"
            )
        }), 400

    campos_requeridos = [
        "nombre",
        "apellido",
        "email",
        "password"
    ]

    for campo in campos_requeridos:

        if not data.get(campo):

            return jsonify({
                "error": (
                    f"El campo '{campo}' "
                    "es obligatorio"
                )
            }), 400

    email = data["email"].strip().lower()

    password = data["password"]

    if not validar_email(email):

        return jsonify({
            "error": "El correo electrónico no es válido"
        }), 400

    if not validar_password(password):

        return jsonify({
            "error": (
                "La contraseña debe tener "
                "al menos 8 caracteres"
            )
        }), 400

    # IMPORTANTE:
    # El registro público SIEMPRE crea pacientes.
    # El cliente no puede elegir admin o medico.

    usuario = registrar_usuario(
        nombre=data["nombre"].strip(),
        apellido=data["apellido"].strip(),
        email=email,
        password=password,
        rol="paciente"
    )

    if usuario is None:

        return jsonify({
            "error": (
                "El correo electrónico "
                "ya está registrado"
            )
        }), 409

    return jsonify({

        "mensaje": (
            "Usuario registrado correctamente"
        ),

        "usuario": {

            "id": usuario.id,

            "nombre": usuario.nombre,

            "apellido": usuario.apellido,

            "email": usuario.email,

            "rol": usuario.rol

        }

    }), 201


@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": (
                "El cuerpo de la solicitud "
                "es obligatorio"
            )
        }), 400

    email = data.get("email")

    password = data.get("password")

    if not email or not password:

        return jsonify({
            "error": (
                "Email y contraseña "
                "son obligatorios"
            )
        }), 400

    email = email.strip().lower()

    usuario = autenticar_usuario(
        email,
        password
    )

    if usuario is None:

        return jsonify({
            "error": "Credenciales incorrectas"
        }), 401

    access_token = create_access_token(

        identity=str(usuario.id),

        additional_claims={
            "rol": usuario.rol
        }

    )

    return jsonify({

        "mensaje": (
            "Inicio de sesión exitoso"
        ),

        "access_token": access_token,

        "usuario": {

            "id": usuario.id,

            "nombre": usuario.nombre,

            "apellido": usuario.apellido,

            "email": usuario.email,

            "rol": usuario.rol

        }

    }), 200


@auth_bp.route(
    "/perfil",
    methods=["GET"]
)
@jwt_required()
def perfil():

    usuario_id = get_jwt_identity()

    usuario = Usuario.query.get(
        int(usuario_id)
    )

    if usuario is None:

        return jsonify({
            "error": "Usuario no encontrado"
        }), 404

    return jsonify({

        "usuario": {

            "id": usuario.id,

            "nombre": usuario.nombre,

            "apellido": usuario.apellido,

            "email": usuario.email,

            "rol": usuario.rol

        }

    }), 200


@auth_bp.route(
    "/admin-prueba",
    methods=["GET"]
)
@requiere_rol("admin")
def admin_prueba():

    return jsonify({

        "mensaje": (
            "Acceso autorizado "
            "para administrador"
        )

    }), 200