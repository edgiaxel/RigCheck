import io
import pytest
from fastapi.testclient import TestClient

from app.config import settings


def test_reject_unsupported_mime_type(auth_client: TestClient):
    file_content = b"Not an image, just text"
    response = auth_client.post(
        "/api/analyze",
        files={"file": ("notes.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert response.status_code == 400
    assert "Invalid image type" in response.json()["detail"]


def test_reject_empty_image(auth_client: TestClient):
    response = auth_client.post(
        "/api/analyze",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_reject_oversized_image(auth_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    # Temporarily set max upload to 1KB to test size limiting safely without huge memory allocations
    monkeypatch.setattr(settings, "max_upload_size_bytes", 1024)

    oversized_data = b"x" * 2048
    response = auth_client.post(
        "/api/analyze",
        files={"file": ("large.jpg", io.BytesIO(oversized_data), "image/jpeg")},
    )
    assert response.status_code == 400
    assert "exceeds maximum allowed size" in response.json()["detail"]


def test_reject_negative_price(auth_client: TestClient, sample_png_bytes: bytes):
    response = auth_client.post(
        "/api/analyze",
        files={"file": ("gpu.png", io.BytesIO(sample_png_bytes), "image/png")},
        data={"price_idr": -100000},
    )
    assert response.status_code == 400
    assert "negative" in response.json()["detail"].lower()
