from datetime import datetime

from app.extensions import db


class Usuario(db.Model):

    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    apellido = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    rol = db.Column(
        db.String(20),
        nullable=False,
        default="paciente"
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    medico = db.relationship(
        "Medico",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )

    citas = db.relationship(
        "Cita",
        back_populates="paciente",
        foreign_keys="Cita.paciente_id"
    )

    def __repr__(self):
        return f"<Usuario {self.email}>"