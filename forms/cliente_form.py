from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=200)])
    cedula = StringField('Cédula', validators=[Optional(), Length(max=20), Regexp(r'^\d*$', message='Solo números')])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20), Regexp(r'^09\d{8}$', message='Debe empezar con 09 y tener 10 dígitos')])
    submit = SubmitField('Guardar')