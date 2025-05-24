import pytest
import json
from bson import ObjectId
from werkzeug.security import generate_password_hash

@pytest.fixture(autouse=True)
def clear_collections(mongo_db):
    # Limpia usuarios y artículos antes de cada prueba
    mongo_db.users.delete_many({})
    mongo_db.articulosMed.delete_many({})

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

    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)

    return user_id

def test_guardar_articulo_exitosamente(client, mongo_db):
    """POST /guardar_articulo debe insertar el artículo correctamente."""
    user_id = login_as(client, mongo_db)

    payload = {
        "codigo": "A001",
        "nombre": "Paracetamol",
        # prueba con cadena separada por comas
        "presentaciones": "500mg, Sachet",
        "categoria": "Analgésico",
        "lote": "L123",
        "fecha_vencimiento": "2025-12-31"
    }
    resp = client.post("/guardar_articulo", json=payload)
    assert resp.status_code == 201, resp.data.decode()
    data = resp.get_json()
    assert data.get("mensaje") == "Artículo guardado exitosamente"

    # Verificar en BD
    art = mongo_db.articulosMed.find_one({"codigo": "A001"})
    assert art is not None
    assert art["nombre"] == "Paracetamol"
    # Debería haberse convertido en lista y recortado
    assert art["presentaciones"] == ["500mg", "Sachet"]
    assert art["categoria"] == "Analgésico"
    assert art["lote"] == "L123"
    # fecha_vencimiento es objeto datetime
    assert hasattr(art["fecha_vencimiento"], "year") and art["fecha_vencimiento"].year == 2025
    # usuario_id vinculado al user_id del login
    assert art["usuario_id"] == user_id
