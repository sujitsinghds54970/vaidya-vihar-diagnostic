from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_patient():
    payload = {
        "name": "John Doe",
        "age": 30,
        "gender": "Male",
        "branch_id": 1
    }
    response = client.post("/api/patients/", json=payload)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
    assert response.status_code == 201
    assert response.json()["name"] == "John Doe"