import re
from typing import Any, Dict, List, Optional

from app.models.analysis import ExtractedSpecifications
from app.models.compatibility import (
    CheckStatus,
    CompatibilityCheckItem,
    CompatibilityReport,
    OverallCompatibilityStatus,
)
from app.models.profile import UserProfile


class CompatibilityEngine:
    """Evaluates verified hardware compatibility rules against user's PC profile."""

    def evaluate(
        self,
        specs: ExtractedSpecifications,
        profile: UserProfile,
        user_price_idr: Optional[int] = None,
    ) -> CompatibilityReport:
        checks: List[CompatibilityCheckItem] = []
        recommendations: List[str] = []

        # 1. Evaluate PSU Wattage
        psu_check = self._check_psu_wattage(specs, profile)
        if psu_check:
            checks.append(psu_check)
            if psu_check.status == CheckStatus.FAIL:
                recommendations.append(
                    f"Upgrade your PSU. This {specs.category or 'component'} requires at least "
                    f"{specs.recommended_psu_watts or specs.power_tdp_watts}W."
                )

        # 2. Evaluate Socket Compatibility (for CPU or Motherboard)
        socket_check = self._check_socket_compatibility(specs, profile)
        if socket_check:
            checks.append(socket_check)
            if socket_check.status == CheckStatus.FAIL:
                recommendations.append(
                    "Motherboard or CPU socket is incompatible. A matching motherboard is required."
                )

        # 3. Evaluate Form Factor (for Case / Motherboard / GPU)
        form_factor_check = self._check_form_factor(specs, profile)
        if form_factor_check:
            checks.append(form_factor_check)

        # 4. Evaluate Budget Constraint
        price_check_data: Optional[Dict[str, Any]] = None
        if user_price_idr is not None or profile.max_budget_idr is not None:
            budget_check, price_check_data = self._check_budget(user_price_idr, profile)
            checks.append(budget_check)
            if budget_check.status in (CheckStatus.FAIL, CheckStatus.WARN):
                recommendations.append("The component price exceeds your configured profile budget.")

        # Determine overall verdict
        overall_status, summary = self._summarize_verdict(checks, specs)

        return CompatibilityReport(
            overall_status=overall_status,
            summary=summary,
            checks=checks,
            price_check=price_check_data,
            recommendations=recommendations,
        )

    def _check_psu_wattage(
        self, specs: ExtractedSpecifications, profile: UserProfile
    ) -> Optional[CompatibilityCheckItem]:
        user_psu = profile.existing_components.psu_wattage
        if (
            user_psu is None
            and profile.compatibility_requirements
            and profile.compatibility_requirements.min_psu_wattage
        ):
            user_psu = profile.compatibility_requirements.min_psu_wattage

        # Only evaluate if this component consumes significant power or specifies requirements
        is_power_component = specs.category in ("GPU", "CPU") or (
            specs.power_tdp_watts is not None or specs.recommended_psu_watts is not None
        )

        if not is_power_component:
            return None

        # Check case 1: Manufacturer recommended PSU wattage is known
        if specs.recommended_psu_watts is not None:
            if user_psu is None:
                return CompatibilityCheckItem(
                    check_name="PSU Wattage Capacity",
                    status=CheckStatus.UNKNOWN,
                    message="Component recommends a "
                    f"{specs.recommended_psu_watts}W PSU, but your profile has no PSU wattage specified.",
                    details={
                        "required_watts": specs.recommended_psu_watts,
                        "profile_psu_watts": None,
                    },
                )

            if user_psu >= specs.recommended_psu_watts:
                return CompatibilityCheckItem(
                    check_name="PSU Wattage Capacity",
                    status=CheckStatus.PASS,
                    message=f"Your {user_psu}W PSU meets the recommended requirement of {specs.recommended_psu_watts}W.",
                    details={
                        "required_watts": specs.recommended_psu_watts,
                        "profile_psu_watts": user_psu,
                        "headroom_watts": user_psu - specs.recommended_psu_watts,
                    },
                )
            else:
                deficit = specs.recommended_psu_watts - user_psu
                return CompatibilityCheckItem(
                    check_name="PSU Wattage Capacity",
                    status=CheckStatus.FAIL,
                    message=f"Your {user_psu}W PSU is {deficit}W below the recommended {specs.recommended_psu_watts}W.",
                    details={
                        "required_watts": specs.recommended_psu_watts,
                        "profile_psu_watts": user_psu,
                        "deficit_watts": deficit,
                    },
                )

        # Check case 2: TDP is known, calculate estimated requirement
        if specs.power_tdp_watts is not None:
            if user_psu is None:
                return CompatibilityCheckItem(
                    check_name="PSU Wattage Capacity",
                    status=CheckStatus.UNKNOWN,
                    message=f"Component TDP is {specs.power_tdp_watts}W, but your profile has no PSU wattage specified.",
                    details={
                        "tdp_watts": specs.power_tdp_watts,
                        "profile_psu_watts": None,
                    },
                )

            # Heuristic: component TDP + 200W base system load + 100W safety headroom
            estimated_min_psu = specs.power_tdp_watts + 250
            if user_psu >= estimated_min_psu:
                return CompatibilityCheckItem(
                    check_name="PSU Wattage Capacity",
                    status=CheckStatus.PASS,
                    message=f"Your {user_psu}W PSU safely accommodates this {specs.power_tdp_watts}W TDP component.",
                    details={
                        "tdp_watts": specs.power_tdp_watts,
                        "profile_psu_watts": user_psu,
                        "estimated_system_draw": estimated_min_psu,
                    },
                )
            elif user_psu >= specs.power_tdp_watts + 150:
                return CompatibilityCheckItem(
                    check_name="PSU Wattage Capacity",
                    status=CheckStatus.WARN,
                    message=f"Your {user_psu}W PSU may operate near maximum load with this {specs.power_tdp_watts}W TDP component.",
                    details={
                        "tdp_watts": specs.power_tdp_watts,
                        "profile_psu_watts": user_psu,
                    },
                )
            else:
                return CompatibilityCheckItem(
                    check_name="PSU Wattage Capacity",
                    status=CheckStatus.FAIL,
                    message=f"Your {user_psu}W PSU is insufficient for a {specs.power_tdp_watts}W TDP component plus system load.",
                    details={
                        "tdp_watts": specs.power_tdp_watts,
                        "profile_psu_watts": user_psu,
                    },
                )

        # Unknown power requirements
        return CompatibilityCheckItem(
            check_name="PSU Wattage Capacity",
            status=CheckStatus.UNKNOWN,
            message="Component power requirements could not be determined with certainty.",
            details={
                "required_watts": None,
                "profile_psu_watts": user_psu,
            },
        )

    def _check_socket_compatibility(
        self, specs: ExtractedSpecifications, profile: UserProfile
    ) -> Optional[CompatibilityCheckItem]:
        if specs.category not in ("CPU", "Motherboard"):
            return None

        profile_socket = None
        if profile.compatibility_requirements and profile.compatibility_requirements.socket:
            profile_socket = profile.compatibility_requirements.socket
        elif profile.existing_components.motherboard:
            # Check for common socket names in motherboard string (e.g. B550 -> AM4, B650 -> AM5, Z790 -> LGA1700)
            mb = profile.existing_components.motherboard.upper()
            if any(k in mb for k in ["AM4", "B450", "B550", "X570", "A520"]):
                profile_socket = "AM4"
            elif any(k in mb for k in ["AM5", "B650", "X670", "A620", "X870"]):
                profile_socket = "AM5"
            elif any(k in mb for k in ["LGA1700", "Z690", "B660", "B760", "Z790"]):
                profile_socket = "LGA1700"
            elif any(k in mb for k in ["LGA1851", "Z890", "B860"]):
                profile_socket = "LGA1851"
            elif any(k in mb for k in ["LGA1200", "Z490", "B460", "B560", "Z590"]):
                profile_socket = "LGA1200"

        if not specs.socket:
            return CompatibilityCheckItem(
                check_name="Socket Compatibility",
                status=CheckStatus.UNKNOWN,
                message="Component socket is unknown or unverified from the label.",
                details={"component_socket": None, "profile_socket": profile_socket},
            )

        if not profile_socket:
            return CompatibilityCheckItem(
                check_name="Socket Compatibility",
                status=CheckStatus.UNKNOWN,
                message=f"Component uses socket {specs.socket}, but user profile has no socket or motherboard specified.",
                details={"component_socket": specs.socket, "profile_socket": None},
            )

        def norm_socket(s: str) -> str:
            return re.sub(r"[^A-Za-z0-9]", "", s).upper()

        if norm_socket(specs.socket) == norm_socket(profile_socket):
            return CompatibilityCheckItem(
                check_name="Socket Compatibility",
                status=CheckStatus.PASS,
                message=f"Socket {specs.socket} matches your profile socket {profile_socket}.",
                details={"component_socket": specs.socket, "profile_socket": profile_socket},
            )
        else:
            return CompatibilityCheckItem(
                check_name="Socket Compatibility",
                status=CheckStatus.FAIL,
                message=f"Socket mismatch: Component requires {specs.socket}, but your system uses {profile_socket}.",
                details={"component_socket": specs.socket, "profile_socket": profile_socket},
            )

    def _check_form_factor(
        self, specs: ExtractedSpecifications, profile: UserProfile
    ) -> Optional[CompatibilityCheckItem]:
        if not specs.form_factor:
            return None

        profile_ff = profile.existing_components.form_factor
        if (
            not profile_ff
            and profile.compatibility_requirements
            and profile.compatibility_requirements.preferred_form_factor
        ):
            profile_ff = profile.compatibility_requirements.preferred_form_factor

        if not profile_ff:
            return CompatibilityCheckItem(
                check_name="Form Factor Verification",
                status=CheckStatus.UNKNOWN,
                message=f"Component form factor is {specs.form_factor}, but no form factor is defined in your profile.",
                details={"component_form_factor": specs.form_factor, "profile_form_factor": None},
            )

        comp_ff = specs.form_factor.upper()
        prof_ff = profile_ff.upper()

        # Mini-ITX cases cannot fit standard ATX boards/components
        if "ITX" in prof_ff and "ATX" in comp_ff and "ITX" not in comp_ff:
            return CompatibilityCheckItem(
                check_name="Form Factor Verification",
                status=CheckStatus.FAIL,
                message=f"Incompatible form factor: {specs.form_factor} component will not fit in an {profile_ff} enclosure.",
                details={"component_form_factor": specs.form_factor, "profile_form_factor": profile_ff},
            )

        if comp_ff in prof_ff or prof_ff in comp_ff:
            return CompatibilityCheckItem(
                check_name="Form Factor Verification",
                status=CheckStatus.PASS,
                message=f"Form factor {specs.form_factor} is compatible with profile {profile_ff}.",
                details={"component_form_factor": specs.form_factor, "profile_form_factor": profile_ff},
            )

        return CompatibilityCheckItem(
            check_name="Form Factor Verification",
            status=CheckStatus.WARN,
            message=f"Check physical clearance: component is {specs.form_factor} and profile specifies {profile_ff}.",
            details={"component_form_factor": specs.form_factor, "profile_form_factor": profile_ff},
        )

    def _check_budget(
        self, user_price_idr: Optional[int], profile: UserProfile
    ) -> tuple[CompatibilityCheckItem, Dict[str, Any]]:
        max_budget = profile.max_budget_idr

        if user_price_idr is None and max_budget is None:
            return (
                CompatibilityCheckItem(
                    check_name="Budget Evaluation",
                    status=CheckStatus.NOT_APPLICABLE,
                    message="No price provided and no maximum budget set in profile.",
                ),
                {},
            )

        if user_price_idr is None:
            return (
                CompatibilityCheckItem(
                    check_name="Budget Evaluation",
                    status=CheckStatus.NOT_APPLICABLE,
                    message=f"Profile has max budget of Rp {max_budget:,}, but no price was entered.",
                    details={"max_budget_idr": max_budget, "entered_price_idr": None},
                ),
                {"max_budget_idr": max_budget, "entered_price_idr": None},
            )

        if max_budget is None:
            return (
                CompatibilityCheckItem(
                    check_name="Budget Evaluation",
                    status=CheckStatus.NOT_APPLICABLE,
                    message=f"Entered price is Rp {user_price_idr:,}. No budget cap configured in profile.",
                    details={"entered_price_idr": user_price_idr, "max_budget_idr": None},
                ),
                {"entered_price_idr": user_price_idr, "max_budget_idr": None},
            )

        diff = max_budget - user_price_idr
        price_info = {
            "entered_price_idr": user_price_idr,
            "max_budget_idr": max_budget,
            "difference_idr": diff,
            "within_budget": diff >= 0,
        }

        if diff >= 0:
            return (
                CompatibilityCheckItem(
                    check_name="Budget Evaluation",
                    status=CheckStatus.PASS,
                    message=f"Price Rp {user_price_idr:,} is within maximum budget of Rp {max_budget:,} (Remaining: Rp {diff:,}).",
                    details=price_info,
                ),
                price_info,
            )
        else:
            over = abs(diff)
            return (
                CompatibilityCheckItem(
                    check_name="Budget Evaluation",
                    status=CheckStatus.WARN,
                    message=f"Price Rp {user_price_idr:,} exceeds maximum budget of Rp {max_budget:,} by Rp {over:,}.",
                    details=price_info,
                ),
                price_info,
            )

    def _summarize_verdict(
        self, checks: List[CompatibilityCheckItem], specs: ExtractedSpecifications
    ) -> tuple[OverallCompatibilityStatus, str]:
        if not checks:
            return (
                OverallCompatibilityStatus.NEEDS_INFO,
                "No definitive compatibility checks could be evaluated with the current profile and label specs.",
            )

        statuses = [c.status for c in checks]

        if CheckStatus.FAIL in statuses:
            failed_checks = [c.check_name for c in checks if c.status == CheckStatus.FAIL]
            return (
                OverallCompatibilityStatus.INCOMPATIBLE,
                f"Component is incompatible with your system due to failed checks: {', '.join(failed_checks)}.",
            )

        if CheckStatus.WARN in statuses:
            warning_checks = [c.check_name for c in checks if c.status == CheckStatus.WARN]
            return (
                OverallCompatibilityStatus.WARNING,
                f"Potential constraints detected in: {', '.join(warning_checks)}. Review details before purchasing.",
            )

        pass_count = statuses.count(CheckStatus.PASS)
        unknown_count = statuses.count(CheckStatus.UNKNOWN)

        if pass_count > 0 and unknown_count == 0:
            return (
                OverallCompatibilityStatus.COMPATIBLE,
                "All evaluated compatibility checks passed successfully against your PC profile.",
            )

        if pass_count > 0 and unknown_count > 0:
            return (
                OverallCompatibilityStatus.WARNING,
                "Partial compatibility confirmed, but some technical parameters remain unverified.",
            )

        return (
            OverallCompatibilityStatus.NEEDS_INFO,
            "Critical specifications are missing or unverified. Cannot confirm full compatibility.",
        )


compatibility_engine = CompatibilityEngine()
