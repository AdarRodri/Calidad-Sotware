from flask import Flask, render_template

from .config import Config
from .extensions import db, jwt, bcrypt


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)


    # MODELOS

    from .models import (
        Usuario,
        Medico,
        Cita
    )


    # RUTAS

    from .routes.auth import auth_bp
    from .routes.usuarios import usuarios_bp
    from .routes.medicos import medicos_bp
    from .routes.citas import citas_bp


    # BLUEPRINTS

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        usuarios_bp
    )

    app.register_blueprint(
        medicos_bp
    )

    app.register_blueprint(
        citas_bp
    )


    # PÁGINA PRINCIPAL

    @app.route("/")
    def inicio():

        return render_template(
            "index.html"
        )


    # CREAR TABLAS

    with app.app_context():

        db.create_all()


    return app