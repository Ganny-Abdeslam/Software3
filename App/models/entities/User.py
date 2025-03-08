from werkzeug.security import check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, fullname="", rut="", profesion="", cargo="", jornada="", sueldo=0.0, fechaNacimiento=None, descuentos=""):
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname
        self.rut = rut
        self.profesion = profesion
        self.cargo = cargo
        self.jornada = jornada
        self.sueldo = sueldo
        self.fechaNacimiento = fechaNacimiento
        self.descuentos = descuentos

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)
