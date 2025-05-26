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
    db_name = f"test_db_{uuid.uuid4().hex}"
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    yield db
    client.drop_database(db_name)

