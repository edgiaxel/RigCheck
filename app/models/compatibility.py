from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.analysis import (
    ExtractedSpecifications,
    PreliminaryAnalysisStatus,
    SearchEnrichment,
    VisionExtractionEvidence,
)


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class OverallCompatibilityStatus(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    WARNING = "WARNING"
    NEEDS_INFO = "NEEDS_INFO"


class CompatibilityCheckItem(BaseModel):
    check_name: str = Field(description="Name of the compatibility rule evaluated")
    status: CheckStatus = Field(description="Check evaluation status")
    message: str = Field(description="Detailed user-facing message explaining the outcome")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured data supporting the verdict (e.g. required vs available watts)"
    )


class CompatibilityReport(BaseModel):
    overall_status: OverallCompatibilityStatus = Field(
        description="Overall verdict across all applicable verified rules"
    )
    summary: str = Field(description="High-level human-readable verdict summary")
    checks: List[CompatibilityCheckItem] = Field(
        default_factory=list,
        description="Breakdown of individual verified compatibility checks"
    )
    price_check: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Budget evaluation if price and profile budget are present"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Targeted suggestions or next actions for the user"
    )


class AnalysisResponse(BaseModel):
    preliminary_status: PreliminaryAnalysisStatus = Field(
        description="High-level vision & data extraction status"
    )
    extracted_specifications: ExtractedSpecifications = Field(
        description="Structured technical specifications extracted from label"
    )
    evidence: VisionExtractionEvidence = Field(
        description="Direct label evidence, visible text, and model codes"
    )
    unresolved_fields: List[str] = Field(
        default_factory=list,
        description="Specifications that could not be determined or verified from label"
    )
    search_enrichment: Optional[SearchEnrichment] = Field(
        default=None,
        description="External technical search results if search was performed"
    )
    compatibility_report: CompatibilityReport = Field(
        description="Evaluation against user's saved PC profile"
    )
    user_price_idr: Optional[int] = Field(
        default=None,
        description="Optional user-provided price in IDR"
    )
    analyzed_at: str = Field(
        description="ISO 8601 timestamp of analysis completion"
    )
