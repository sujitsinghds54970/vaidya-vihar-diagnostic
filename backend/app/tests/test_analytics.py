from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_admin_summary():
    response = client.get("/admin/summary", headers={"Authorization": "Bearer <admin_token>"})
    assert response.status_code == 200
    data = response.json()
    assert "total_patients" in data
    assert "total_revenue" in data
    assert "total_tests" in data

def test_branch_summary():
    response = client.get("/admin/branch-summary", headers={"Authorization": "Bearer <admin_token>"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)