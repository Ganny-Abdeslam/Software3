from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, DateTimeField, DateField
from wtforms.validators import DataRequired, Length

class ArticuloForm(FlaskForm):
    codigo = StringField("Código", validators=[DataRequired()])
    nombre = StringField("Nombre", validators=[DataRequired()])
    presentaciones = StringField("Presentaciones", validators=[DataRequired()])
    categoria = SelectField("Categoría", choices=[('medicamento', 'Medicamento'), ('servicio', 'Servicio'), ('insumo', 'Insumo')])
    lote = StringField("Lote", validators=[DataRequired()])
    fecha_vencimiento = DateField("Fecha de Vencimiento", format='%Y-%m-%d', validators=[DataRequired()])

class BodegaForm(FlaskForm):
    nombre = StringField("Nombre de la Bodega", validators=[DataRequired()])
    submit = SubmitField("Crear Bodega")


class CitasForm(FlaskForm):
    identificacion = StringField("Identificación del paciente", validators=[DataRequired(), Length(min=4, max=20)])
    paciente = StringField("Paciente", validators=[DataRequired()])
    fecha_hora= DateTimeField("Fecha y Hora", format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    motivo = TextAreaField("Motivo de la Cita", validators=[DataRequired()])
    submit = SubmitField("Agendar Cita")
    estado = StringField("Estado", validators=[DataRequired()])