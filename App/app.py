from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from config import config
from datetime import datetime
from forms import ArticuloForm, BodegaForm, CitasForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_mail import Mail, Message
from bson.json_util import dumps

from models.User import User

app = Flask(__name__)

# Configuración de MongoDB
app.config.from_object(config['development'])
mongo = PyMongo(app)
collection = mongo.db.Software3

csrf = CSRFProtect(app)
login_manager_app = LoginManager(app)
login_manager_app.login_view = "login"

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Cambia si usas otro proveedor
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'avanzadanegocios@gmail.com'
app.config['MAIL_PASSWORD'] = 'iamd zvnp ucuj ifpg'
app.config['MAIL_DEFAULT_SENDER'] = 'avanzadanegocios@gmail.com'

mail = Mail(app)

menu_items = [
    {"name": "Agregar Artículo", "url": "articulo", "disabled": False},
    {"name": "Administrar Bodegas", "url": "bodegas", "disabled": False},
    {"name": "Agendar Citas", "url": "citas", "disabled": False},
    {"name": "Ver Citas", "url": "listaCitas", "disabled": False},
    {"name": "Administrar Citas", "url": "admin_citas", "disabled": False},
    {"name": "Facturar", "url": "factura", "disabled": False}
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
        lote = data.get("lote")
        fecha_vencimiento = data.get("fecha_vencimiento")

        if not all([codigo, nombre, presentaciones, categoria]):
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        if isinstance(presentaciones, str):
            presentaciones_list = [p.strip() for p in presentaciones.split(",")]
        elif isinstance(presentaciones, list):
            presentaciones_list = [p.strip() for p in presentaciones]
        else:
            return jsonify({"error": "El campo 'presentaciones' debe ser una lista o una cadena de texto"}), 400

        try:
            fecha_vencimiento_dt = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "El formato de fecha debe ser YYYY-MM-DD"}), 400

        articulo = {
            "codigo": codigo,
            "nombre": nombre,
            "presentaciones": presentaciones_list,
            "categoria": categoria,
            "lote": lote,
            "fecha_vencimiento": fecha_vencimiento_dt,
            "usuario_id": ObjectId(current_user.id)
        }

        mongo.db.articulosMed.insert_one(articulo)

        return jsonify({"mensaje": "Artículo guardado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Hubo un problema al guardar el artículo: {str(e)}"}), 500

@app.route('/listar_articulos', methods=['GET'])
@login_required
def listar_articulos():
    try:
        articulos = list(mongo.db.articulosMed.find({"usuario_id": ObjectId(current_user.id)}))
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
        print("📨 Formulario recibido:", request.form)
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
            articulo = mongo.db.articulosMed.find_one({"_id": articulo_id}, {"nombre": 1})
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

@app.route("/profesionales", methods=["GET"])
@login_required
def obtener_profesionales():
    try:
        profesionales = mongo.db.users.find({}, {"fullname": 1})
        lista = [{"id": str(p["_id"]), "nombre": p["fullname"]} for p in profesionales]
        return jsonify(lista), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/guardar_cita", methods=["POST"])
@login_required
def guardar_cita():
    print(request.get_json())
    try:
        if not request.is_json:
            return jsonify({"error": "Solicitud debe ser JSON"}), 400

        data = request.get_json()
        print("DATA RECIBIDA:", data)

        paciente_id = data.get("paciente_id")
        paciente = data.get("paciente")
        email = data.get("email")
        fecha_hora = data.get("fecha_hora")
        motivo = data.get("motivo")
        sitio = data.get("sitio")  # sitio enviado desde el frontend

        if not all([paciente_id, paciente, fecha_hora, motivo, sitio]):
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        # Buscar el nombre completo del profesional
        user_data = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
        profesional = user_data.get("fullname", "Desconocido")

        cita = {
            "paciente_id": paciente_id,
            "paciente": paciente,
            "email": email,
            "fecha_hora": fecha_hora,
            "motivo": motivo,
            "sitio": sitio,
            "profesional": profesional,
            "estado": "A",  # por defecto activa
            "usuario_id": ObjectId(current_user.id)
        }

        mongo.db.citas.insert_one(cita)

        # Enviar correo de confirmación
        try:
            msg = Message(
                subject="Confirmación de Cita",
                recipients=[email],  # o data.get("email") si viene desde el formulario
                body=f"Hola {paciente}, tu cita ha sido agendada para el {fecha_hora}.\nMotivo: {motivo}"
            )
            mail.send(msg)
            print("📧 Correo enviado correctamente")
        except Exception as e:
            print(f"❌ Error al enviar el correo: {e}")

        return jsonify({"mensaje": "Cita guardada exitosamente"}), 201

    except Exception as e:
        print("Error al guardar la cita:", e)
        return jsonify({"error": f"Hubo un error al guardar la cita: {str(e)}"}), 500

@app.route("/listar_citas", methods=["GET"])
@login_required
def listar_citas():
    try:
        # Obtener todas las citas de la base de datos
        citas = list(mongo.db.citas.find({"estado": "A"}))
        return dumps(citas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/listaCitas")
@login_required
def listaCitasView():
    form = CitasForm()
    return render_template("listarCitas.html", menu_items=menu_items, form=form)

@app.route("/citas")
@login_required
def cita():
    form = CitasForm()
    return render_template("cita.html", menu_items=menu_items, form=form)

@app.route("/admin_citas")
@login_required
def admin_citas_view():
    form = CitasForm()
    return render_template("adminCitas.html", menu_items=menu_items, form=form)

@app.route("/mis_citas", methods=["GET"])
@login_required
def obtener_mis_citas():
    try:
        citas = list(mongo.db.citas.find({
            "usuario_id": ObjectId(current_user.id),
            "estado": "A"
        }))
        return dumps(citas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/actualizar_cita/<cita_id>", methods=["PUT"])
@login_required
def actualizar_cita(cita_id):
    try:
        data = request.get_json()
        fecha_hora = data.get("fecha_hora")
        motivo = data.get("motivo")
        estado = data.get("estado")

        if not all([fecha_hora, motivo, estado]):
            return jsonify({"error": "Todos los campos son requeridos"}), 400

        resultado = mongo.db.citas.update_one(
            {
                "_id": ObjectId(cita_id),
                "usuario_id": ObjectId(current_user.id)
            },
            {
                "$set": {
                    "fecha_hora": fecha_hora,
                    "motivo": motivo,
                    "estado": estado
                }
            }
        )

        if resultado.matched_count == 0:
            return jsonify({"error": "Cita no encontrada o no autorizada"}), 404

        return jsonify({"mensaje": "Cita actualizada correctamente"}), 200

    except Exception as e:
        print("Error actualizando cita:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/atender_cita/<cita_id>", methods=["PUT"])
@login_required
@csrf.exempt
def atender_cita(cita_id):
    try:
        cita = mongo.db.citas.find_one({
            "_id": ObjectId(cita_id),
            "usuario_id": ObjectId(current_user.id)
        })

        if not cita:
            return jsonify({"error": "No se encontró la cita"}), 404

        # Actualizar el estado
        result = mongo.db.citas.update_one(
            {"_id": ObjectId(cita_id)},
            {"$set": {"estado": "atendido"}}
        )

        if result.modified_count == 1:
            # Enviar correo al paciente
            email = cita.get("email")
            paciente = cita.get("paciente")
            fecha_hora = cita.get("fecha_hora")

            if email:
                try:
                    msg = Message(
                        subject="📬 Tu cita fue atendida",
                        recipients=[email],
                        body=f"Hola {paciente},\n\nTu cita programada para el {fecha_hora} ha sido marcada como *atendida*.\n\nGracias por confiar en nosotros.\n\nMedControl"
                    )
                    mail.send(msg)
                    print("📧 Correo de atención enviado correctamente")
                except Exception as e:
                    print(f"❌ Error al enviar el correo de atención: {e}")
            else:
                print("⚠️ La cita no tiene correo asociado, no se puede enviar notificación")

            return jsonify({"mensaje": "Cita marcada como atendida"}), 200
        else:
            return jsonify({"error": "No se pudo actualizar el estado de la cita"}), 500

    except Exception as e:
        print("❌ Error en atender_cita:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/factura')
@login_required
def factura():
    docs = mongo.db.bodegas.find()
    bodegas = [{
        "_id": str(b["_id"]),
        "nombre": b["nombre"]
    } for b in docs]

    print("Bodegas cargadas:", bodegas)  # Debug

    return render_template(
        'factura.html',
        menu_items=menu_items,
        bodegas=bodegas
    )

@app.route('/generar_factura', methods=['POST'])
@login_required
@csrf.exempt
def generar_factura():
    try:
        data = request.get_json()
        # Validar payload
        email = data.get('email')
        bodega_id = data.get('bodega_id')
        costo_consulta = data.get('costo_consulta')
        items = data.get('items', [])

        if not all([email, bodega_id, isinstance(items, list)]):
            return jsonify({'error': 'Datos incompletos'}), 400

        # Convertir IDs y preparar factura
        user_id = ObjectId(current_user.id)
        b_id = ObjectId(bodega_id)

        # Insertar factura en la base de datos
        factura_doc = {
            'usuario_id': user_id,
            'bodega_id': b_id,
            'email_paciente': email,
            'costo_consulta': costo_consulta,
            'items': [],
            'total': 0,
            'fecha': datetime.utcnow()
        }
        total = costo_consulta

        # Procesar cada artículo: deducir inventario y acumular totales
        for it in items:
            art_id = ObjectId(it['articulo_id'])
            cantidad = int(it['cantidad'])
            precio = float(it.get('precio', 0))
            subtotal = cantidad * precio
            total += subtotal

            factura_doc['items'].append({
                'articulo_id': art_id,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal
            })

            # Deducir inventario en la bodega
            mongo.db.bodegas.update_one(
                {'_id': b_id, 'inventario.articulo': art_id},
                {'$inc': {'inventario.$.cantidad': -cantidad}}
            )

        # Actualizar total
        factura_doc['total'] = total
        mongo.db.facturas.insert_one(factura_doc)

        # Construir cuerpo de correo
        lineas = [f"Factura generada:\nConsulta: ${costo_consulta:.2f}\n"]
        for x in factura_doc['items']:
            art = mongo.db.articulosMed.find_one({'_id': x['articulo_id']}, {'nombre': 1})
            nombre = art['nombre'] if art else str(x['articulo_id'])
            lineas.append(f"- {nombre}: {x['cantidad']} x ${x['precio']:.2f} = ${x['subtotal']:.2f}")
        lineas.append(f"\nTotal: ${total:.2f}")
        cuerpo = "\n".join(lineas)

        # Enviar correo al paciente
        msg = Message(
            subject='📄 Su factura Med Control',
            recipients=[email],
            body=cuerpo
        )
        mail.send(msg)

        return jsonify({'mensaje': 'Factura generada, guardada y enviada por correo'}), 201

    except Exception as e:
        print(f"Error en generar_factura: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/obtener_inventarioFact/<bodega_id>', methods=['GET'])
@login_required
@csrf.exempt
def obtener_inventario_detallado(bodega_id):
    """Devuelve lista de artículos en una bodega con id, nombre, cantidad y precio."""
    bodega = mongo.db.bodegas.find_one({"_id": ObjectId(bodega_id)})
    if not bodega:
        return jsonify({"error": "Bodega no encontrada"}), 404

    inventario = bodega.get("inventario", [])
    resultado = []
    for item in inventario:
        # item["articulo"] es un ObjectId en Mongo
        art_id = ObjectId(item["articulo"])
        art_doc = mongo.db.articulosMed.find_one(
            {"_id": art_id},
            {"nombre": 1, "precio": 1}  # asumiendo que guardas precio en articulosMed
        )
        if not art_doc:
            continue
        resultado.append({
            "articulo_id": str(art_id),
            "nombre": art_doc["nombre"],
            "cantidad": item["cantidad"],
            "precio": float(art_doc.get("precio", 0))
        })

    return jsonify({"articulos": resultado}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
