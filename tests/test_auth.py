import pytest
from fastapi.testclient import TestClient


def test_login_successful(client: TestClient):
    response = client.post("/api/auth/login", json={"secret": "anything"})
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "session_token" in data


def test_endpoints_open_without_auth(client: TestClient):
    # Profile GET is open
    resp_get = client.get("/api/profile")
    assert resp_get.status_code == 200
    assert "existing_components" in resp_get.json()

    # Profile PUT is open
    resp_put = client.put("/api/profile", json={"profile_name": "Open Station Test"})
    assert resp_put.status_code == 200
    assert resp_put.json()["profile_name"] == "Open Station Test"


def test_logout_endpoint(client: TestClient):
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200


def test_cross_origin_cors_headers(client: TestClient):
    # Render static site origin
    render_opt = client.options(
        "/api/health",
        headers={
            "Origin": "https://rigcheck.onrender.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert render_opt.status_code == 200
    assert render_opt.headers.get("access-control-allow-origin") == "https://rigcheck.onrender.com"
    assert render_opt.headers.get("access-control-allow-credentials") == "true"

    # Cloudflare tunnel origin
    cf_opt = client.options(
        "/api/health",
        headers={
            "Origin": "https://hardware-station.trycloudflare.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert cf_opt.status_code == 200
    assert cf_opt.headers.get("access-control-allow-origin") == "https://hardware-station.trycloudflare.com"
