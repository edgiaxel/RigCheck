import io
from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.profile_storage import ProfileStorageService, profile_storage


@pytest.fixture
def temp_profile_storage(tmp_path: Path) -> Generator[ProfileStorageService, None, None]:
    """Provides an isolated profile storage service backed by a temporary directory."""
    temp_file = tmp_path / "test_user_profile.json"
    service = ProfileStorageService(storage_path=str(temp_file))
    original_storage = profile_storage.storage_path
    profile_storage.storage_path = temp_file
    yield service
    profile_storage.storage_path = original_storage


@pytest.fixture
def client(temp_profile_storage: ProfileStorageService) -> TestClient:
    """FastAPI TestClient with isolated profile storage (unauthenticated)."""
    return TestClient(app)


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """FastAPI TestClient authenticated with a valid session cookie."""
    secret = settings.get_effective_access_secret()
    login_resp = client.post("/api/auth/login", json={"secret": secret})
    assert login_resp.status_code == 200
    token = login_resp.json()["session_token"]
    client.cookies.set("rigcheck_session", token)
    return client


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Minimal valid 1x1 PNG bytes."""
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00"
        b"\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    """Minimal valid JPEG header bytes."""
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xd9"
