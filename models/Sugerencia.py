# models/sugerencia.py

from datetime import datetime
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from models.Database import db

class Sugerencia(db.Model):
    __tablename__ = 'sugerencias'

    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(100), nullable=False)
    mensaje   = db.Column(db.Text,        nullable=False)
    creado_el = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Sugerencia {self.id} | {self.nombre}>'

class SugerenciaForm(FlaskForm):
    nombre    = StringField(
        'Nombre',
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(max=100, message="Máximo 100 caracteres")
        ]
    )
    mensaje   = TextAreaField(
        'Tu sugerencia',
        validators=[
            DataRequired(message="El mensaje es obligatorio"),
            Length(min=10, max=2000,
            message="El mensaje debe tener entre 10 y 2000 caracteres")
        ]
    )
    recaptcha = RecaptchaField()
    submit    = SubmitField('Enviar sugerencia')


