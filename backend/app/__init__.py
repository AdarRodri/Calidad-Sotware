import os

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, jwt, bcrypt


def _origenes_permitidos():
    """FRONTEND_URL: URL(s) del frontend separadas por coma. Sin definir, permite cualquiera."""
    valor = os.getenv("FRONTEND_URL", "*").strip()
    if valor == "*":
        return "*"
    return [o.strip().rstrip("/") for o in valor.split(",") if o.strip()]


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # CORS: permite que el frontend (otro dominio) llame a la API.
    CORS(app, resources={r"/api/*": {"origins": _origenes_permitidos()}})


    # MODELOS

    from .models import (
        Usuario,
        Medico,
        Cita,
        HistoriaClinica,
        Recordatorio
    )


    # RUTAS

    from .routes.auth import auth_bp
    from .routes.usuarios import usuarios_bp
    from .routes.medicos import medicos_bp
    from .routes.citas import citas_bp
    from .routes.historias import historias_bp
    from .routes.recordatorios import recordatorios_bp
    from .routes.reportes import reportes_bp


    # BLUEPRINTS

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(medicos_bp)
    app.register_blueprint(citas_bp)
    app.register_blueprint(historias_bp)
    app.register_blueprint(recordatorios_bp)
    app.register_blueprint(reportes_bp)


    # RAÍZ DE LA API (comprobar que el servidor está activo)

    @app.route("/")
    def inicio():
        return jsonify({
            "servicio": "MediCitas API",
            "estado": "ok"
        }), 200


    # CREAR TABLAS

    with app.app_context():

        db.create_all()


    return app
