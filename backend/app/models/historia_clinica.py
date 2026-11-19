from app.extensions import db
from app.utils.tiempo import ahora


class HistoriaClinica(db.Model):
    """Atención médica de una cita: diagnóstico, evolución y observaciones."""

    __tablename__ = "historias_clinicas"

    id = db.Column(db.Integer, primary_key=True)

    # Una cita tiene como máximo una historia clínica.
    cita_id = db.Column(
        db.Integer,
        db.ForeignKey("citas.id"),
        unique=True,
        nullable=False
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

    diagnostico = db.Column(db.Text, nullable=False)
    evolucion = db.Column(db.Text, nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    fecha_registro = db.Column(db.DateTime, default=ahora)
    fecha_actualizacion = db.Column(db.DateTime, default=ahora, onupdate=ahora)

    cita = db.relationship("Cita")
    paciente = db.relationship("Usuario", foreign_keys=[paciente_id])
    medico = db.relationship("Medico")

    def __repr__(self):
        return f"<HistoriaClinica {self.id}>"
