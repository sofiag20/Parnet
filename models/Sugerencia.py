from models.Database import db
from datetime import datetime


class Sugerencia(db.Model):
    __tablename__ = 'sugerencias'

    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(100), nullable=False)
    mensaje   = db.Column(db.Text,        nullable=False)
    creado_el = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Sugerencia {self.id} | {self.nombre}>'
