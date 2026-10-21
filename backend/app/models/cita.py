from datetime import datetime

from app.extensions import db


class Cita(db.Model):

    __tablename__ = "citas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    medico_id = db.Column(
        db.Integer,
        db.ForeignKey("medicos.id"),
        nullable=False
    )

    fecha_hora = db.Column(
        db.DateTime,
        nullable=False
    )

    motivo = db.Column(
        db.String(500),
        nullable=True
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="programada"
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    paciente = db.relationship(
        "Usuario",
        back_populates="citas",
        foreign_keys=[paciente_id]
    )

    medico = db.relationship(
        "Medico",
        back_populates="citas"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "medico_id",
            "fecha_hora",
            name="uq_medico_fecha_hora"
        ),
    )

    def __repr__(self):
        return f"<Cita {self.id}>"