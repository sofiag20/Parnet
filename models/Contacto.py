from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactoForm(FlaskForm):
    nombre  = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    correo  = StringField('Correo electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    asunto  = StringField('Asunto', validators=[DataRequired(), Length(max=100)])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10, max=2000)])
    submit  = SubmitField('Enviar')
