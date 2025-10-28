from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dummy():
    response = client.get("/")# Replace with any working GET route
    assert response.status_code in [200, 404]