from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductoForm(FlaskForm):
    slug = StringField('Slug', validators=[DataRequired(), Length(max=100)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=200)])
    precio = FloatField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    img = StringField('URL de imagen', validators=[Length(max=500)])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField('Guardar')