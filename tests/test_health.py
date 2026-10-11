from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "RigCheck Backend"
    assert data["authenticated"] is True
    assert "ollama" in data
    assert "storage" in data
    assert "search_service" in data
