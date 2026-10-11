from app.models.analysis import ExtractedSpecifications
from app.models.compatibility import (
    CheckStatus,
    OverallCompatibilityStatus,
)
from app.models.profile import (
    CompatibilityRequirements,
    ExistingComponents,
    UserProfile,
)
from app.services.compatibility import CompatibilityEngine


def test_psu_wattage_sufficient_pass():
    engine = CompatibilityEngine()
    specs = ExtractedSpecifications(
        category="GPU",
        brand="NVIDIA",
        model="RTX 4070",
        recommended_psu_watts=650,
    )
    profile = UserProfile(
        existing_components=ExistingComponents(psu_wattage=750)
    )

    report = engine.evaluate(specs, profile)
    psu_check = next(c for c in report.checks if c.check_name == "PSU Wattage Capacity")
    assert psu_check.status == CheckStatus.PASS
    assert "meets" in psu_check.message
    assert report.overall_status == OverallCompatibilityStatus.COMPATIBLE


def test_psu_wattage_insufficient_fail():
    engine = CompatibilityEngine()
    specs = ExtractedSpecifications(
        category="GPU",
        brand="NVIDIA",
        model="RTX 4080",
        recommended_psu_watts=750,
    )
    profile = UserProfile(
        existing_components=ExistingComponents(psu_wattage=500)
    )

    report = engine.evaluate(specs, profile)
    psu_check = next(c for c in report.checks if c.check_name == "PSU Wattage Capacity")
    assert psu_check.status == CheckStatus.FAIL
    assert "below" in psu_check.message
    assert report.overall_status == OverallCompatibilityStatus.INCOMPATIBLE
    assert any("Upgrade your PSU" in rec for rec in report.recommendations)


def test_psu_wattage_missing_specs_unknown():
    engine = CompatibilityEngine()
    specs = ExtractedSpecifications(
        category="GPU",
        brand="Unknown",
        model="Custom Card",
        recommended_psu_watts=None,
        power_tdp_watts=None,
    )
    profile = UserProfile(
        existing_components=ExistingComponents(psu_wattage=600)
    )

    report = engine.evaluate(specs, profile)
    psu_check = next(c for c in report.checks if c.check_name == "PSU Wattage Capacity")
    assert psu_check.status == CheckStatus.UNKNOWN
    assert report.overall_status == OverallCompatibilityStatus.NEEDS_INFO


def test_socket_match_pass():
    engine = CompatibilityEngine()
    specs = ExtractedSpecifications(
        category="CPU",
        brand="AMD",
        model="Ryzen 7 7800X3D",
        socket="AM5",
    )
    profile = UserProfile(
        existing_components=ExistingComponents(motherboard="ASUS TUF B650-PLUS")
    )

    report = engine.evaluate(specs, profile)
    socket_check = next(c for c in report.checks if c.check_name == "Socket Compatibility")
    assert socket_check.status == CheckStatus.PASS


def test_socket_mismatch_fail():
    engine = CompatibilityEngine()
    specs = ExtractedSpecifications(
        category="CPU",
        brand="AMD",
        model="Ryzen 7 7800X3D",
        socket="AM5",
    )
    profile = UserProfile(
        existing_components=ExistingComponents(motherboard="MSI B450 Tomahawk")
    )

    report = engine.evaluate(specs, profile)
    socket_check = next(c for c in report.checks if c.check_name == "Socket Compatibility")
    assert socket_check.status == CheckStatus.FAIL
    assert report.overall_status == OverallCompatibilityStatus.INCOMPATIBLE


def test_form_factor_incompatible_fail():
    engine = CompatibilityEngine()
    specs = ExtractedSpecifications(
        category="Motherboard",
        form_factor="ATX",
    )
    profile = UserProfile(
        existing_components=ExistingComponents(form_factor="Mini-ITX")
    )

    report = engine.evaluate(specs, profile)
    ff_check = next(c for c in report.checks if c.check_name == "Form Factor Verification")
    assert ff_check.status == CheckStatus.FAIL
    assert report.overall_status == OverallCompatibilityStatus.INCOMPATIBLE


def test_budget_evaluation_within_and_exceeded():
    engine = CompatibilityEngine()
    specs = ExtractedSpecifications(category="RAM")
    profile = UserProfile(max_budget_idr=2000000)

    # Within budget
    report_pass = engine.evaluate(specs, profile, user_price_idr=1500000)
    budget_check_pass = next(c for c in report_pass.checks if c.check_name == "Budget Evaluation")
    assert budget_check_pass.status == CheckStatus.PASS
    assert budget_check_pass.details["within_budget"] is True

    # Exceeding budget
    report_warn = engine.evaluate(specs, profile, user_price_idr=2500000)
    budget_check_warn = next(c for c in report_warn.checks if c.check_name == "Budget Evaluation")
    assert budget_check_warn.status == CheckStatus.WARN
    assert budget_check_warn.details["within_budget"] is False
    assert report_warn.overall_status == OverallCompatibilityStatus.WARNING
