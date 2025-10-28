from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_invoice():
    payload = {
        "patient_id": 1,
        "branch_id": 1,
        "total_amount": 500.0
    }
    create_response = client.post("/invoices/", json=payload)
    assert create_response.status_code == 201
    invoice_id = create_response.json()["id"]

    get_response = client.get(f"/invoices/{invoice_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["total_amount"] == 500.0