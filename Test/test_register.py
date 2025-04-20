def test_register_user(client, mongo_db):
    # Datos simulados del formulario
    form_data = {
        "name": "Test User",
        "rut": "12345678-9",
        "profesion": "Médico",
        "fecha": "1990-01-01",
        "email": "testuser@example.com",
        "password": "securepassword"
    }

    # Enviar datos tipo form y no json
    response = client.post("/register", data=form_data, content_type='application/x-www-form-urlencoded', follow_redirects=True)

    assert response.status_code == 200
    assert b'Cuenta creada exitosamente' in response.data

    # Validar en la base de datos
    usuario = mongo_db.users.find_one({"email": "testuser@example.com"})
    assert usuario is not None
    assert usuario["fullname"] == "Test User"
