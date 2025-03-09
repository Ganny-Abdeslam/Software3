from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField  
from wtforms.validators import DataRequired

class ArticuloForm(FlaskForm):
    codigo = StringField("Código", validators=[DataRequired()])
    nombre = StringField("Nombre", validators=[DataRequired()])
    presentaciones = StringField("Presentaciones", validators=[DataRequired()])
    categoria = SelectField("Categoría", choices=[('medicamento', 'Medicamento'), ('servicio', 'Servicio'), ('insumo', 'Insumo')])

class BodegaForm(FlaskForm):
    nombre = StringField("Nombre de la Bodega", validators=[DataRequired()])
    submit = SubmitField("Crear Bodega")