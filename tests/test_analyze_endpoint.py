import io
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.models.analysis import (
    ExtractedSpecifications,
    PreliminaryAnalysisStatus,
    SearchEnrichment,
    VisionExtractionEvidence,
)


def test_analyze_endpoint_success(auth_client: TestClient, sample_png_bytes: bytes):
    mock_specs = ExtractedSpecifications(
        category="GPU",
        brand="ASUS",
        model="Dual GeForce RTX 4070 OC",
        recommended_psu_watts=650,
        power_tdp_watts=200,
    )
    mock_evidence = VisionExtractionEvidence(
        visible_labels=["ASUS", "DUAL", "RTX 4070"],
        part_or_model_number="DUAL-RTX4070-O12G",
    )
    mock_unresolved = []
    mock_status = PreliminaryAnalysisStatus.EXTRACTED
    mock_search = SearchEnrichment(
        performed=True,
        query="ASUS Dual GeForce RTX 4070 OC specs",
        sources=["TechPowerUp RTX 4070 Specs"],
        resolved_fields=["recommended_psu_watts"],
        search_summary="Verified 650W PSU requirement",
    )

    # First update profile with a 750W PSU and 12,000,000 IDR budget
    auth_client.put(
        "/api/profile",
        json={
            "profile_name": "Test Rig",
            "existing_components": {"psu_wattage": 750},
            "max_budget_idr": 12000000,
        },
    )

    with patch(
        "app.routers.analyze.ollama_client.extract_from_image",
        new_callable=AsyncMock,
    ) as mock_extract:
        mock_extract.return_value = (
            mock_specs,
            mock_evidence,
            mock_unresolved,
            mock_status,
            mock_search,
        )

        response = auth_client.post(
            "/api/analyze",
            files={"file": ("label.png", io.BytesIO(sample_png_bytes), "image/png")},
            data={"price_idr": 10500000, "enable_search": True},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["preliminary_status"] == "EXTRACTED"
        assert data["extracted_specifications"]["brand"] == "ASUS"
        assert data["extracted_specifications"]["model"] == "Dual GeForce RTX 4070 OC"
        assert data["evidence"]["part_or_model_number"] == "DUAL-RTX4070-O12G"
        assert data["search_enrichment"]["performed"] is True
        assert data["user_price_idr"] == 10500000

        compat = data["compatibility_report"]
        assert compat["overall_status"] == "COMPATIBLE"
        assert len(compat["checks"]) >= 2  # PSU check + Budget check
