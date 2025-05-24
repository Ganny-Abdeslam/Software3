def test_register_user_simplificado(mongo_db):
    from werkzeug.security import generate_password_hash
    from datetime import datetime

    # Simular lo que hace /register
    test_email = "testuser@example.com"
    mongo_db.users.delete_many({"email": test_email})

    user_data = {
        "fullname": "Test User",
        "rut": "12345678-9",
        "profesion": "Médico",
        "fechaNacimiento": datetime.strptime("1990-01-01", "%Y-%m-%d"),
        "email": test_email,
        "password": generate_password_hash("securepassword")
    }

    mongo_db.users.insert_one(user_data)

    user = mongo_db.users.find_one({"email": test_email})
    assert user is not None
    assert user["fullname"] == "Test User"
