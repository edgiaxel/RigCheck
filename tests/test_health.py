from fastapi.testclient import TestClient


def test_health_endpoint_unauthenticated(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "RigCheck Backend"
    assert data["authenticated"] is False
    # Verifies internal storage paths and Ollama model lists are NOT exposed publicly
    assert "storage" not in data
    assert "ollama" not in data


def test_health_endpoint_authenticated(auth_client: TestClient):
    response = auth_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "ollama" in data
    assert "storage" in data
    assert "search_service" in data
