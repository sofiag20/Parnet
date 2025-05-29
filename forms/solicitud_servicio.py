from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class ServicioForm(FlaskForm):
    area    = SelectField('Área', coerce=int, validators=[DataRequired()])
    detalle = TextAreaField(
        'Detalle del servicio',
        validators=[DataRequired(message="Indica qué necesitas"), Length(min=10)]
    )
    recaptcha = RecaptchaField()
    submit    = SubmitField('Enviar solicitud')
