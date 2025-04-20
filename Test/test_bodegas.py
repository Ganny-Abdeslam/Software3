def test_crear_bodega_exitoso(client, mongo_db):
    # Simular un usuario en la base de datos
    user = User(username='testuser', password='password')  # Asegúrate de usar tu modelo de usuario
    mongo_db.users.insert_one(user.__dict__)  # Inserta el usuario en la base de datos

    # Loguear al usuario simulado
    login_user(user)

    response = client.post(
        "/crear_bodega",
        json={"nombre": "Bodega Central"}
    )

    assert response.status_code == 201
    assert "Bodega creada exitosamente" in response.get_json().get("mensaje")
