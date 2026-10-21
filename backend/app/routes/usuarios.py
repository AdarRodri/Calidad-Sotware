from flask import Blueprint, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from app.models.usuario import Usuario


usuarios_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/api/usuarios"
)


@usuarios_bp.route(
    "/me",
    methods=["GET"]
)
@jwt_required()
def obtener_mi_usuario():

    usuario_id = get_jwt_identity()

    usuario = Usuario.query.get(
        int(usuario_id)
    )

    if usuario is None:

        return jsonify({
            "error": "Usuario no encontrado"
        }), 404

    return jsonify({

        "id": usuario.id,

        "nombre": usuario.nombre,

        "apellido": usuario.apellido,

        "email": usuario.email,

        "rol": usuario.rol,

        "fecha_creacion": (
            usuario.fecha_creacion.isoformat()
            if usuario.fecha_creacion
            else None
        )

    }), 200