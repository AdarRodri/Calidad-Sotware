from app.extensions import db, bcrypt
from app.models.usuario import Usuario


def registrar_usuario(
    nombre,
    apellido,
    email,
    password,
    rol="paciente"
):

    usuario_existente = Usuario.query.filter_by(
        email=email
    ).first()

    if usuario_existente:
        return None

    password_hash = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        password_hash=password_hash,
        rol=rol
    )

    db.session.add(usuario)
    db.session.commit()

    return usuario


def autenticar_usuario(email, password):

    usuario = Usuario.query.filter_by(
        email=email
    ).first()

    if not usuario:
        return None

    password_correcta = bcrypt.check_password_hash(
        usuario.password_hash,
        password
    )

    if not password_correcta:
        return None

    return usuario