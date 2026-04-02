from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp

class UsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=200)])
    mail = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20), Regexp(r'^09\d{8}$', message='Debe empezar con 09 y tener 10 dígitos')])
    password = PasswordField('Contraseña', validators=[Optional()])  # opcional en edición
    rol = SelectField('Rol', choices=[('cliente', 'Cliente'), ('admin', 'Administrador')], validators=[DataRequired()])
    submit = SubmitField('Guardar')