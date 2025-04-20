def test_guardar_articulo(client, mongo_db):
    articulo_data = {
        "codigo": "A123",
        "nombre": "Paracetamol",
        "presentaciones": "500mg, 1g",
        "categoria": "Analgésico",
        "lote": "L123456",
        "fecha_vencimiento": "2025-12-31"
    }

    response = client.post("/guardar_articulo", json=articulo_data)

    assert response.status_code == 201
    assert "Artículo guardado exitosamente" in response.data.decode("utf-8")

    articulo = mongo_db.articulosMed.find_one({"codigo": "A123"})
    assert articulo is not None
    assert articulo["nombre"] == "Paracetamol"
    assert "500mg" in articulo["presentaciones"]
