from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf import CSRFProtect

mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(testing=False):
    app = Flask(__name__)
    app.config['MONGO_URI'] = "mongodb://localhost:27017/clinica_test" if testing else "mongodb://localhost:27017/software3"
    app.config['TESTING'] = testing
    flask_app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_ENABLED'] = False  # << desactiva CSRF para pruebas
    app.secret_key = "admin"

    mongo.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints aquí...

    return app