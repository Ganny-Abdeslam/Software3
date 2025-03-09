from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from config import config
from datetime import datetime
from forms import ArticuloForm, BodegaForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

from models.User import User

app = Flask(__name__)

# Configuración de MongoDB
app.config.from_object(config['development'])
mongo = PyMongo(app)
collection = mongo.db.Software3

csrf = CSRFProtect(app)
login_manager_app = LoginManager(app)
login_manager_app.login_view = "login"

menu_items = [
    {"name": "Agregar Artículo", "url": "articulo", "disabled": False},
    {"name": "Administrar Bodegas", "url": "bodegas", "disabled": False}
    ]

@login_manager_app.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User.from_mongo(user_data) if user_data else None
    except Exception as e:
        print(f"Error al cargar usuario: {e}")
        return None

@app.route('/')
def layout():
    return render_template('index.html', menu_items=menu_items)

@app.route('/articulo')
@login_required
def articulo():
    form = ArticuloForm()  # Crea una instancia del formulario
    articulos = listar_articulos()  # Función que recupera los artículos desde la base de datos
    return render_template('articulo.html', menu_items=menu_items, articulos=articulos, form=form)

@app.route('/guardar_articulo', methods=['POST'])
@login_required
def guardar_articulo():
    try:
        if not request.is_json:
            return jsonify({"error": "La solicitud debe ser JSON"}), 415

        data = request.get_json()

        codigo = data.get("codigo")
        nombre = data.get("nombre")
        presentaciones = data.get("presentaciones")
        categoria = data.get("categoria")

        if not all([codigo, nombre, presentaciones, categoria]):
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        if isinstance(presentaciones, str):
            presentaciones_list = [p.strip() for p in presentaciones.split(",")]
        elif isinstance(presentaciones, list):
            presentaciones_list = [p.strip() for p in presentaciones]
        else:
            return jsonify({"error": "El campo 'presentaciones' debe ser una lista o una cadena de texto"}), 400

        articulo = {
            "codigo": codigo,
            "nombre": nombre,
            "presentaciones": presentaciones_list,
            "categoria": categoria,
            "usuario_id": ObjectId(current_user.id)
        }

        mongo.db.articulos.insert_one(articulo)

        return jsonify({"mensaje": "Artículo guardado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Hubo un problema al guardar el artículo: {str(e)}"}), 500

@app.route('/listar_articulos', methods=['GET'])
@login_required
def listar_articulos():
    try:
        articulos = list(mongo.db.articulos.find({"usuario_id": ObjectId(current_user.id)}))
        for articulo in articulos:
            articulo["_id"] = str(articulo["_id"])
        return jsonify({"articulos": articulos}), 200
    except Exception as e:
        print(f"Error al listar artículos: {e}")
        return jsonify({"error": "Hubo un problema al obtener los artículos"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = mongo.db.users.find_one({"email": email})

        if user_data and check_password_hash(user_data["password"], password):
            user = User.from_mongo(user_data)
            login_user(user)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('layout'))
        else:
            flash("Credenciales incorrectas", 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre, rut, profesion, fecha_nacimiento, email, password = (
            request.form.get('name'),
            request.form.get('rut'),
            request.form.get('profesion'),
            request.form.get('fecha'),
            request.form.get('email'),
            request.form.get('password')
        )

        if not all([nombre, rut, profesion, fecha_nacimiento, email, password]):
            flash('Por favor complete todos los campos.', 'danger')
            return redirect(url_for('register'))

        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return redirect(url_for('register'))

        if mongo.db.users.find_one({"email": email}):
            flash('El correo ya está registrado.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        
        mongo.db.users.insert_one({
            "fullname": nombre,
            "rut": rut,
            "profesion": profesion,
            "fechaNacimiento": fecha_nacimiento,
            "email": email,
            "password": hashed_password
        })

        flash('Cuenta creada exitosamente!', 'success')
        return redirect(url_for('login'))

    return render_template('registrar.html')

@app.route('/profile')
@login_required
def profile():
    user_data = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
    if user_data:
        return render_template('profile.html', menu_items=menu_items, user=user_data)
    flash("No se pudo cargar el perfil", "danger")
    return redirect(url_for('layout'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))

@app.errorhandler(401)
def status_401(error):
    return redirect(url_for('login'))

@app.errorhandler(404)
def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

@app.route("/listar_bodegas", methods=["GET"])
@login_required
def listar_bodegas():
    try:
        bodegas = list(mongo.db.bodegas.find({}, {"nombre": 1}))  # Solo devuelve nombre e ID
        for bodega in bodegas:
            bodega["_id"] = str(bodega["_id"])  # Convertir ObjectId a string

        return jsonify({"bodegas": bodegas}), 200

    except Exception as e:
        print(f"❌ Error al listar bodegas: {e}")
        return jsonify({"error": "No se pudieron obtener las bodegas"}), 500

def listar_bodega(bodega_id):
    """Busca una bodega por su ID en MongoDB."""
    return mongo.db.bodegas.find_one({"_id": ObjectId(bodega_id)})

@app.route("/crear_bodega", methods=["POST"])
@login_required
def crear_bodega():
    try:
        if not request.is_json:  # Verificar si realmente es JSON
            print("❌ La solicitud no tiene formato JSON válido.")
            return jsonify({"error": "El contenido debe ser JSON"}), 400

        data = request.get_json(silent=True)  # silent=True evita que Flask lance errores
        print("🔍 Datos recibidos en /crear_bodega:", data)  

        if not data:
            return jsonify({"error": "No se recibieron datos o el JSON es inválido"}), 400

        nombre = data.get("nombre")
        if not nombre:
            return jsonify({"error": "El nombre de la bodega es obligatorio"}), 400

        usuario_id = ObjectId(current_user.id) if ObjectId.is_valid(current_user.id) else None
        if not usuario_id:
            return jsonify({"error": "ID de usuario inválido"}), 400

        nueva_bodega = {"nombre": nombre, "usuario_id": usuario_id}
        resultado = mongo.db.bodegas.insert_one(nueva_bodega)

        if resultado.inserted_id:
            print(f"✅ Bodega creada con ID: {resultado.inserted_id}")
            return jsonify({"mensaje": "Bodega creada exitosamente"}), 201

        return jsonify({"error": "No se pudo crear la bodega"}), 500

    except Exception as e:
        print(f"❌ Error en /crear_bodega: {e}")
        return jsonify({"error": f"Hubo un problema al crear la bodega: {str(e)}"}), 500


@app.route('/agregar_articulo_bodega', methods=['POST'])
@csrf.exempt
def agregar_articulo_bodega():
    try:
        data = request.json
        csrf_token = request.headers.get("X-CSRFToken")
        print(data)
        bodega_id = data.get("bodegaId")
        articulo = data.get("articuloId")
        cantidad = data.get("cantidad")

        if not bodega_id or not articulo or cantidad is None:
            return jsonify({"error": "Faltan datos"}), 400

        bodega = listar_bodega(bodega_id)
        if not bodega:
            return jsonify({"error": "Bodega no encontrada"}), 404

        # Actualizar el inventario
        mongo.db.bodegas.update_one(
            {"_id": ObjectId(bodega_id)},
            {"$push": {"inventario": {"articulo": articulo, "cantidad": cantidad}}}
        )

        return jsonify({"mensaje": "Artículo agregado con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/obtener_inventario/<bodega_id>', methods=['GET'])
def obtener_inventario(bodega_id):
    try:
        bodega = listar_bodega(bodega_id)  # Obtener la bodega desde MongoDB
        if not bodega:
            return jsonify({"error": "Bodega no encontrada"}), 404

        inventario = bodega.get("inventario", [])  # Extraer inventario o devolver lista vacía
        print("📦 Inventario sin procesar:", inventario)  # <-- DEBUG

        # Buscar los nombres de los artículos en MongoDB
        for item in inventario:
            articulo_id = ObjectId(item["articulo"])
            articulo = mongo.db.articulos.find_one({"_id": articulo_id}, {"nombre": 1})
            item["articulo"] = articulo["nombre"] if articulo else "Artículo desconocido"

        print("📦 Inventario procesado:", inventario)  # <-- DEBUG
        return jsonify({"articulos": inventario}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/bodegas")
@login_required
def bodega():
    form = BodegaForm()
    return render_template("bodega.html", menu_items=menu_items, form=form)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
