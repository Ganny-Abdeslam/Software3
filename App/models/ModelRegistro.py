from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ModelRegistro(db.Model):
    __tablename__ = 'registro'  # El nombre de la tabla en MySQL

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(255), nullable=False)
    profesion = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(255), nullable=False)
    jornada = db.Column(db.String(255), nullable=False)
    sueldo = db.Column(db.Float, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    descuentos = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Registro {self.nombre}>"
