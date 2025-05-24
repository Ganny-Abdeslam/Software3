import pytest
from bson import ObjectId
from werkzeug.security import generate_password_hash

@pytest.fixture(autouse=True)
def clear_collections(mongo_db):
    mongo_db.users.delete_many({})
    mongo_db.bodegas.delete_many({})

def test_crear_bodega_exitosamente(client, mongo_db):
    # 1) Prepara y guarda un usuario de prueba
    user_id = ObjectId()
    usuario = {
        "_id": user_id,
        "email": "usuario@prueba.com",
        "password": generate_password_hash("pass123"),
        "fullname": "Usuario Prueba",
        "profesion": "Tester"
    }
    mongo_db.users.insert_one(usuario)

    # 2) Simula el login inyectando el user_id en la sesión
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)

    # 3) Llama al endpoint /crear_bodega
    payload = {"nombre": "Bodega Central"}
    resp = client.post("/crear_bodega", json=payload)

    # 4) Comprueba código y existencia en BD
    assert resp.status_code == 201, resp.data.decode()
    body = resp.get_json()
    assert body.get("mensaje") == "Bodega creada exitosamente"

    # 5) Verifica que el documento esté realmente en la colección
    b = mongo_db.bodegas.find_one({"nombre": "Bodega Central"})
    assert b is not None
    assert b["usuario_id"] == user_id
