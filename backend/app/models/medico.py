from app.extensions import db


class Medico(db.Model):

    __tablename__ = "medicos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        unique=True,
        nullable=False
    )

    especialidad = db.Column(
        db.String(100),
        nullable=False
    )

    telefono = db.Column(
        db.String(30),
        nullable=True
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="medico"
    )

    citas = db.relationship(
        "Cita",
        back_populates="medico",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Medico {self.id}>"