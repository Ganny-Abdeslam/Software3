def test_guardar_cita(client):
    cita_data = {
        "paciente_id": "1234567890",
        "paciente": "Juan Pérez",
        "email": "juan@example.com",
        "fecha_hora": "2025-04-30T10:00",
        "motivo": "Control general",
        "profesional": "Dr. Andrés Morales",
        "sitio": "Sede Norte"
    }

    response = client.post("/guardar_cita", json=cita_data)
    assert response.status_code == 200 or response.status_code == 201
    data = response.get_json()
    assert data.get("message") == "Cita guardada correctamente"
