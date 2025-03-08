from flask import Flask, render_template, request, flash, redirect, url_for
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from config import config
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId

from models.ModelUser import ModelUser
from models.entities.User import User

app = Flask(__name__)

# Configuración de MongoDB
app.config.from_object(config['development'])
mongo = PyMongo(app)

csrf = CSRFProtect(app)
login_manager_app = LoginManager(app)

menu_items = [
    # {"name": "Elegir Método de Pago", "url": "metodoPago", "disabled": False},
    # {"name": "Revisar Información Empleado", "url": "profile", "disabled": False},
    # {"name": "Revisar Días Trabajador", "url": "dias", "disabled": False},
    # {"name": "Revisar Cotizaciones", "url": "cotizacion", "disabled": False},
    # {"name": "Imprimir Liquidación", "url": "#", "disabled": False},
]

@login_manager_app.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    return User.from_mongo(user_data) if user_data else None

@app.route('/')
def layout():
    return render_template('index.html', menu_items=menu_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_data = mongo.db.users.find_one({"email": email})
        if user_data and user_data["password"] == password:
            user = User.from_mongo(user_data)
            login_user(user)
            return redirect(url_for('layout'))
        else:
            flash("Usuario o contraseña incorrectos", 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('name')
        rut = request.form.get('rut')
        profesion = request.form.get('profesion')
        fecha_nacimiento = datetime.strptime(request.form.get('fecha'), '%Y-%m-%d')
        email = request.form.get('email')
        descuentos = request.form.get('descuentos')

        if not nombre or not rut or not profesion or not fecha_nacimiento or not email or not descuentos:
            flash('Por favor complete todos los campos.', 'danger')
            return redirect(url_for('register'))

        try:
            mongo.db.users.insert_one({
                "fullname": nombre,
                "rut": rut,
                "profesion": profesion,
                "cargo": cargo,
                "fechaNacimiento": fecha_nacimiento,
                "email": email,
                "password": "admin"
            })

            flash('Cuenta creada exitosamente!', 'success')
            return redirect(url_for('layout'))

        except Exception as e:
            flash(f'Error al crear la cuenta: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('registrar.html', menu_items=menu_items)

@app.route('/profile')
@login_required
def profile():
    user_data = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
    if user_data:
        return render_template('profile.html', menu_items=menu_items, user=user_data)
    else:
        flash("No se pudo cargar el perfil", "danger")
        return redirect(url_for('layout'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(401)
def status_401(error):
    return redirect(url_for('login'))

@app.errorhandler(404)
def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == '__main__':
    app.run(debug=True)
