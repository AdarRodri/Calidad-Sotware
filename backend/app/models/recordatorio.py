from app.extensions import db
from app.utils.tiempo import ahora


class Recordatorio(db.Model):
    """Recordatorio enviado al paciente antes de su cita (uno por cita)."""

    __tablename__ = "recordatorios"

    id = db.Column(db.Integer, primary_key=True)

    cita_id = db.Column(
        db.Integer,
        db.ForeignKey("citas.id", ondelete="CASCADE"),
        nullable=False
    )

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    tipo = db.Column(db.String(20), nullable=False, default="previo")

    mensaje = db.Column(db.String(400), nullable=False)

    # enviado | error | no_configurado
    estado_correo = db.Column(db.String(20), nullable=False, default="no_configurado")

    fecha_creacion = db.Column(db.DateTime, default=ahora)

    cita = db.relationship("Cita")

    __table_args__ = (
        db.UniqueConstraint("cita_id", "tipo", name="uq_recordatorio_cita_tipo"),
    )

    def __repr__(self):
        return f"<Recordatorio {self.id}>"
