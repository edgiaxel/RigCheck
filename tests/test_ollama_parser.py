import pytest
from app.models.analysis import ExtractedSpecifications, PreliminaryAnalysisStatus
from app.services.ollama_client import (
    OllamaVisionClient,
    extract_json_from_text,
)


def test_extract_json_from_plain_text():
    raw = '{"brand": "ASUS", "model": "RTX 4070 Dual", "category": "GPU"}'
    data = extract_json_from_text(raw)
    assert data["brand"] == "ASUS"
    assert data["model"] == "RTX 4070 Dual"
    assert data["category"] == "GPU"


def test_extract_json_from_markdown_fenced_block():
    raw = """Here is the extracted information from the hardware label:
```json
{
  "category": "GPU",
  "brand": "MSI",
  "model": "GeForce RTX 3060 Ventus 2X",
  "power_tdp_watts": 170,
  "recommended_psu_watts": 550,
  "socket": null,
  "visible_labels": ["MSI", "RTX 3060", "VENTUS 2X"]
}
```
Hope this helps!"""
    data = extract_json_from_text(raw)
    assert data["brand"] == "MSI"
    assert data["power_tdp_watts"] == 170
    assert data["socket"] is None
    assert len(data["visible_labels"]) == 3


def test_extract_json_malformed_raises_value_error():
    with pytest.raises(ValueError):
        extract_json_from_text("This is pure text with no JSON at all.")

    with pytest.raises(ValueError):
        extract_json_from_text("")


def test_audit_unresolved_fields_preserves_uncertainty():
    client = OllamaVisionClient()
    specs = ExtractedSpecifications(
        category="GPU",
        brand="NVIDIA",
        model="Founders Edition",
        power_tdp_watts=None,        # Missing on label
        recommended_psu_watts=None,  # Missing on label
    )
    unresolved = []

    client._audit_unresolved_fields(specs, unresolved)

    # Must explicitly list power_tdp_watts and recommended_psu_watts as unresolved, NEVER guess
    assert "power_tdp_watts" in unresolved
    assert "recommended_psu_watts" in unresolved
    assert specs.power_tdp_watts is None
    assert specs.recommended_psu_watts is None


def test_evaluate_status_insufficient_data():
    client = OllamaVisionClient()
    specs = ExtractedSpecifications()
    status = client._evaluate_status(specs, None)
    assert status == PreliminaryAnalysisStatus.INSUFFICIENT_DATA


def test_evaluate_status_extracted():
    client = OllamaVisionClient()
    specs = ExtractedSpecifications(category="GPU", brand="Gigabyte", model="Eagle OC")
    status = client._evaluate_status(specs, None)
    assert status == PreliminaryAnalysisStatus.EXTRACTED


def test_evaluate_status_partially_identified():
    client = OllamaVisionClient()
    specs = ExtractedSpecifications(category="GPU", brand="ASUS", model=None)
    status = client._evaluate_status(specs, None)
    assert status == PreliminaryAnalysisStatus.PARTIALLY_IDENTIFIED
