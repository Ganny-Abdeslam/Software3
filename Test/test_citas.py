import pytest
import json
from bson import ObjectId
from werkzeug.security import generate_password_hash

@pytest.fixture(autouse=True)
def clear_collections(mongo_db):
    # Limpiar usuarios y citas antes de cada test
    mongo_db.users.delete_many({})
    mongo_db.citas.delete_many({})

def login_as(client, mongo_db):
    """
    Helper para crear un usuario de prueba e inyectar su sesión.
    Devuelve el ObjectId del usuario.
    """
    user_id = ObjectId()
    usuario = {
        "_id": user_id,
        "email": "testuser@example.com",
        "password": generate_password_hash("password123"),
        "fullname": "Test User",
        "profesion": "Doctor"
    }
    mongo_db.users.insert_one(usuario)

    # Forzar login
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)

    return user_id

def test_guardar_cita_exitosamente(client, mongo_db, monkeypatch):
    """POST /guardar_cita debe insertar la cita y “enviar” el correo."""
    user_id = login_as(client, mongo_db)

    # Stub para que mail.send no falle
    from app import mail
    monkeypatch.setattr(mail, "send", lambda msg: True)

    payload = {
        "paciente_id": "1234567890",
        "paciente": "Juan Pérez",
        "email": "juan@example.com",
        "fecha_hora": "2025-04-30T10:00",
        "motivo": "Control general",
        "sitio": "Sede Norte"
    }
    resp = client.post("/guardar_cita", json=payload)
    assert resp.status_code == 201, resp.data.decode()
    assert resp.get_json() == {"mensaje": "Cita guardada exitosamente"}

    # Verificar en DB
    cita = mongo_db.citas.find_one({"paciente": "Juan Pérez"})
    assert cita is not None
    assert cita["usuario_id"] == user_id
    assert cita["motivo"] == "Control general"
    assert cita["sitio"] == "Sede Norte"

def test_listar_citas(client, mongo_db):
    """GET /listar_citas debe devolver todas las citas con estado 'A'."""
    user_id = login_as(client, mongo_db)

    # Insertar varias citas, unas activas y otras no
    docs = [
        {"paciente": "A", "estado": "A", "usuario_id": user_id},
        {"paciente": "B", "estado": "atendido", "usuario_id": user_id},
        {"paciente": "C", "estado": "A", "usuario_id": ObjectId()}
    ]
    mongo_db.citas.insert_many(docs)

    resp = client.get("/listar_citas")
    assert resp.status_code == 200
    data = json.loads(resp.get_data(as_text=True))
    # Debe incluir las dos citas con estado A (tanto la del mismo user como de otro)
    pacientes = {c["paciente"] for c in data}
    assert pacientes == {"A", "C"}

def test_obtener_mis_citas(client, mongo_db):
    """GET /mis_citas debe devolver solo las citas activas del usuario actual."""
    user_id = login_as(client, mongo_db)

    # Insertar citas de este usuario y de otro
    own = [
        {"paciente": "X", "estado": "A", "usuario_id": user_id},
        {"paciente": "Y", "estado": "A", "usuario_id": user_id},
        {"paciente": "Z", "estado": "atendido", "usuario_id": user_id},
    ]
    other = [
        {"paciente": "O1", "estado": "A", "usuario_id": ObjectId()}
    ]
    mongo_db.citas.insert_many(own + other)

    resp = client.get("/mis_citas")
    assert resp.status_code == 200
    data = json.loads(resp.get_data(as_text=True))
    pacientes = {c["paciente"] for c in data}
    # Solo las activas del usuario
    assert pacientes == {"X", "Y"}
