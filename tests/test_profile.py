import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.models.profile import UserProfile, ExistingComponents, IntendedUpgrade, CompatibilityRequirements
from app.services.profile_storage import ProfileStorageService


def test_get_default_profile(auth_client: TestClient):
    response = auth_client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["profile_name"] == "My PC Rig"
    assert data["existing_components"]["cpu"] is None


def test_save_and_retrieve_profile(auth_client: TestClient):
    payload = {
        "profile_name": "Axel Gaming Battlestation",
        "existing_components": {
            "cpu": "AMD Ryzen 5 5600X",
            "gpu": "NVIDIA GTX 1660 Super",
            "motherboard": "Gigabyte B550M DS3H",
            "ram": "16GB DDR4 3200MHz",
            "psu_wattage": 550,
            "psu_model": "Corsair CV550 80+ Bronze",
            "case_model": "Deepcool CC560",
            "form_factor": "Micro-ATX",
        },
        "intended_upgrade": {
            "target_category": "GPU",
            "target_model": "RTX 4070",
            "notes": "Upgrade for 1440p gaming"
        },
        "compatibility_requirements": {
            "min_psu_wattage": 650,
            "preferred_form_factor": "Micro-ATX",
            "socket": "AM4",
            "max_gpu_length_mm": 370
        },
        "max_budget_idr": 10000000
    }

    put_response = auth_client.put("/api/profile", json=payload)
    assert put_response.status_code == 200
    saved_data = put_response.json()
    assert saved_data["profile_name"] == "Axel Gaming Battlestation"
    assert saved_data["existing_components"]["psu_wattage"] == 550
    assert saved_data["max_budget_idr"] == 10000000
    assert saved_data["updated_at"] is not None

    get_response = auth_client.get("/api/profile")
    assert get_response.status_code == 200
    retrieved = get_response.json()
    assert retrieved["profile_name"] == "Axel Gaming Battlestation"
    assert retrieved["intended_upgrade"]["target_category"] == "GPU"
    assert retrieved["compatibility_requirements"]["socket"] == "AM4"


def test_profile_validation_rejects_negative_budget(auth_client: TestClient):
    payload = {
        "profile_name": "Test Rig",
        "max_budget_idr": -500000
    }
    response = auth_client.put("/api/profile", json=payload)
    assert response.status_code == 422


def test_profile_storage_corrupted_json_recovery(tmp_path: Path):
    corrupt_file = tmp_path / "corrupt_profile.json"
    corrupt_file.write_text("{invalid_json: true,,", encoding="utf-8")

    storage = ProfileStorageService(storage_path=str(corrupt_file))
    profile = storage.get_profile()
    assert profile is not None
    assert "Recovered" in profile.profile_name
