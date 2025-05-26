import sys
import os

# Añade el path para que Python pueda encontrar App/app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'App')))

from app import app as flask_app # importa la instancia "app" directamente

import pytest

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['LOGIN_DISABLED'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as client:
        yield client

@pytest.fixture
def mongo_db():
    from app import mongo
    yield mongo.db
    mongo.db.users.delete_many({})

