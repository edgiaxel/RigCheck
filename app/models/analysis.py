from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PreliminaryAnalysisStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    PARTIALLY_IDENTIFIED = "PARTIALLY_IDENTIFIED"
    UNCERTAIN = "UNCERTAIN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ExtractedSpecifications(BaseModel):
    category: Optional[str] = Field(
        default=None,
        description="Component category (e.g. GPU, CPU, Motherboard, PSU, RAM, Storage, Cooler, Case)"
    )
    brand: Optional[str] = Field(
        default=None,
        description="Brand / Manufacturer (e.g. ASUS, NVIDIA, AMD, Corsair, MSI, Gigabyte)"
    )
    model: Optional[str] = Field(
        default=None,
        description="Specific model name (e.g. GeForce RTX 4070 Dual OC, Ryzen 5 5600X)"
    )
    series_or_chipset: Optional[str] = Field(
        default=None,
        description="Architecture or chipset family (e.g. RTX 40-series, B650, AM5)"
    )
    power_tdp_watts: Optional[int] = Field(
        default=None,
        description="Rated TDP or total power consumption in Watts"
    )
    recommended_psu_watts: Optional[int] = Field(
        default=None,
        description="Manufacturer recommended minimum PSU wattage"
    )
    socket: Optional[str] = Field(
        default=None,
        description="CPU or Motherboard socket type (e.g. AM4, AM5, LGA1700, LGA1851)"
    )
    form_factor: Optional[str] = Field(
        default=None,
        description="Form factor (e.g. ATX, Micro-ATX, Mini-ITX, SFX, 2.5-slot)"
    )
    memory_spec: Optional[str] = Field(
        default=None,
        description="Memory details (e.g. 12GB GDDR6X, 32GB DDR5 6000MHz)"
    )
    interface_or_slot: Optional[str] = Field(
        default=None,
        description="Bus interface (e.g. PCIe 4.0 x16, M.2 NVMe PCIe 4.0)"
    )
    dimensions_or_clearance: Optional[str] = Field(
        default=None,
        description="Physical dimensions if visible (e.g. 267 x 134 x 51 mm)"
    )
    power_connectors: Optional[str] = Field(
        default=None,
        description="Required power cables (e.g. 1x 16-pin 12VHPWR, 2x 8-pin PCIe)"
    )
    other_visible_specs: Dict[str, str] = Field(
        default_factory=dict,
        description="Any additional explicitly visible parameters"
    )


class VisionExtractionEvidence(BaseModel):
    visible_labels: List[str] = Field(
        default_factory=list,
        description="Text fragments and model codes read directly from the component or box label"
    )
    part_or_model_number: Optional[str] = Field(
        default=None,
        description="Exact MPN / part code found on the label (e.g. DUAL-RTX4070-O12G)"
    )
    confidence_notes: Optional[str] = Field(
        default=None,
        description="Observations regarding label clarity, lighting, or partial occlusion"
    )


class SearchEnrichment(BaseModel):
    performed: bool = Field(
        default=False,
        description="Whether an online search was triggered"
    )
    query: Optional[str] = Field(
        default=None,
        description="Search query executed against SerpAPI"
    )
    sources: List[str] = Field(
        default_factory=list,
        description="Titles and links of referenced search results"
    )
    resolved_fields: List[str] = Field(
        default_factory=list,
        description="Specification fields resolved via search enrichment"
    )
    search_summary: Optional[str] = Field(
        default=None,
        description="Brief summary of findings from technical reference search"
    )


class RawVisionExtraction(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    series_or_chipset: Optional[str] = None
    power_tdp_watts: Optional[int] = None
    recommended_psu_watts: Optional[int] = None
    socket: Optional[str] = None
    form_factor: Optional[str] = None
    memory_spec: Optional[str] = None
    interface_or_slot: Optional[str] = None
    dimensions_or_clearance: Optional[str] = None
    power_connectors: Optional[str] = None
    other_visible_specs: Dict[str, str] = Field(default_factory=dict)
    visible_labels: List[str] = Field(default_factory=list)
    part_or_model_number: Optional[str] = None
    confidence_notes: Optional[str] = None
    unresolved_fields: List[str] = Field(default_factory=list)
    preliminary_status: Optional[str] = None
