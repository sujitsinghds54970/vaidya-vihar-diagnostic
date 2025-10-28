from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_lab_result():
    payload = {
        "test_name": "Hemoglobin",
        "result_value": 13.5,
        "unit": "g/dL",
        "reference_range": "12.0 - 16.0",
        "invoice_id": 1,
        "patient_id": 1
    }
    create_response = client.post("/lab-results/", json=payload)
    assert create_response.status_code == 201
    result_id = create_response.json()["id"]

    get_response = client.get(f"/lab-results/{payload['patient_id']}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert any(r["id"] == result_id for r in data)