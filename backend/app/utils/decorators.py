from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt
)


def requiere_rol(*roles_permitidos):

    def decorador(funcion):

        @wraps(funcion)
        def funcion_protegida(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            rol_usuario = claims.get("rol")

            if rol_usuario not in roles_permitidos:

                return jsonify({
                    "error": (
                        "No tienes permisos para "
                        "realizar esta operación"
                    )
                }), 403

            return funcion(*args, **kwargs)

        return funcion_protegida

    return decorador