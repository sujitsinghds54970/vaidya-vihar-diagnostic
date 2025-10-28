from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_invoice():
    payload = {
        "patient_id": 1,
        "amount": 500.0
    }
    response = client.post("/invoices/", json=payload)
    assert response.status_code == 201
    assert response.json()["amount"] == 500.0
    assert response.json()["status"] == "unpaid"