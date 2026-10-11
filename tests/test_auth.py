import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.services.auth_service import auth_service


def test_login_successful(client: TestClient):
    secret = settings.get_effective_access_secret()
    response = client.post("/api/auth/login", json={"secret": secret})
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert "session_token" in data
    assert "rigcheck_session" in response.cookies


def test_login_rejected_with_wrong_secret(client: TestClient):
    response = client.post("/api/auth/login", json={"secret": "wrong-secret-guess"})
    assert response.status_code == 401
    assert "Invalid access secret" in response.json()["detail"]


def test_rate_limiting_lockout(client: TestClient):
    # Simulate failed attempts up to limit
    for _ in range(settings.max_failed_auth_attempts):
        client.post("/api/auth/login", json={"secret": "wrong-pass"})

    # Next attempt should be blocked with 429
    blocked_resp = client.post("/api/auth/login", json={"secret": "wrong-pass"})
    assert blocked_resp.status_code == 429
    assert "Too many failed login attempts" in blocked_resp.json()["detail"]

    # Reset failure tracking for test hygiene
    auth_service._failed_attempts.clear()


def test_unauthenticated_access_rejected_on_endpoints(client: TestClient):
    # Profile GET
    resp_get = client.get("/api/profile")
    assert resp_get.status_code == 401
    assert "Authentication required" in resp_get.json()["detail"]

    # Profile PUT
    resp_put = client.put("/api/profile", json={"profile_name": "Hack Attempt"})
    assert resp_put.status_code == 401

    # Analyze POST
    resp_post = client.post("/api/analyze")
    assert resp_post.status_code == 401


def test_logout_revokes_session(client: TestClient):
    secret = settings.get_effective_access_secret()
    login_resp = client.post("/api/auth/login", json={"secret": secret})
    token = login_resp.json()["session_token"]

    # Verify authenticated
    status_resp1 = client.get("/api/auth/status")
    assert status_resp1.json()["authenticated"] is True

    # Logout
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["authenticated"] is False

    # Verify now unauthenticated
    status_resp2 = client.get("/api/auth/status")
    assert status_resp2.json()["authenticated"] is False


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

    # Untrusted domain should be rejected by CORS
    bad_opt = client.options(
        "/api/health",
        headers={
            "Origin": "https://unauthorized-domain.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert bad_opt.status_code == 400
    assert "access-control-allow-origin" not in bad_opt.headers

