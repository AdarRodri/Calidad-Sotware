"""Crea la cuenta de administrador en la base de datos configurada (local o en la nube).

Uso (Git Bash), apuntando a la base de datos en la nube:
    DATABASE_URL="postgresql://usuario:clave@host/db?sslmode=require" python crear_admin.py

El correo y la contraseña se piden por teclado (la contraseña no se muestra).
También puedes definir ADMIN_EMAIL y ADMIN_PASSWORD como variables de entorno.
"""
import getpass
import os
import sys

from app import create_app
from app.extensions import db, bcrypt
from app.models.usuario import Usuario


def main():
    email = (os.getenv("ADMIN_EMAIL") or input("Correo del administrador: ")).strip().lower()
    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Contraseña (mínimo 8 caracteres): ")
    nombre = os.getenv("ADMIN_NOMBRE", "Administrador")
    apellido = os.getenv("ADMIN_APELLIDO", "MediCitas")

    if "@" not in email:
        sys.exit("El correo no es válido.")
    if len(password) < 8:
        sys.exit("La contraseña debe tener al menos 8 caracteres.")

    app = create_app()  # También crea las tablas si todavía no existen.
    with app.app_context():
        if Usuario.query.filter_by(email=email).first() is not None:
            sys.exit("Ya existe una cuenta con ese correo. No se modificó nada.")

        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            rol="admin",
        )
        db.session.add(usuario)
        db.session.commit()
        print(f"Administrador creado correctamente: {email}")


if __name__ == "__main__":
    main()
