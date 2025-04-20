def create_app(testing=False):
    app = Flask(__name__)
    app.config['MONGO_URI'] = "mongodb://localhost:27017/clinica_test" if testing else "mongodb://localhost:27017/software3"
    app.config['TESTING'] = testing
    app.secret_key = "admin"

    mongo.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints aquí...

    return app
