from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_appointment():
    payload = {
        "patient_id": 1,
        "calendar_day_id": 1,
        "time_slot": "10:30:00"
    }
    create_response = client.post("/appointments/", json=payload)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["id"]

    get_response = client.get(f"/appointments/by-day/{payload['calendar_day_id']}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert any(a["id"] == appointment_id for a in data)