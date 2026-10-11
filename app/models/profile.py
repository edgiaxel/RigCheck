from typing import Optional
from pydantic import BaseModel, Field


class ExistingComponents(BaseModel):
    cpu: Optional[str] = Field(default=None, description="Current CPU model, e.g. AMD Ryzen 5 5600X")
    gpu: Optional[str] = Field(default=None, description="Current GPU model, e.g. GTX 1660 Super")
    motherboard: Optional[str] = Field(default=None, description="Current Motherboard model, e.g. B550M")
    ram: Optional[str] = Field(default=None, description="Current RAM specs, e.g. 16GB DDR4 3200MHz")
    psu_wattage: Optional[int] = Field(default=None, description="Power supply wattage, e.g. 550")
    psu_model: Optional[str] = Field(default=None, description="Power supply model rating, e.g. Corsair CV550")
    case_model: Optional[str] = Field(default=None, description="PC Case model, e.g. Deepcool CC560")
    form_factor: Optional[str] = Field(default=None, description="Form factor, e.g. ATX, Micro-ATX, Mini-ITX")
    additional_notes: Optional[str] = Field(default=None, description="Additional component notes")


class IntendedUpgrade(BaseModel):
    target_category: Optional[str] = Field(default=None, description="Target component category, e.g. GPU, CPU, RAM")
    target_model: Optional[str] = Field(default=None, description="Specific target component model name")
    notes: Optional[str] = Field(default=None, description="Desired upgrade requirements or goals")


class CompatibilityRequirements(BaseModel):
    min_psu_wattage: Optional[int] = Field(default=None, description="Minimum PSU headroom requirement")
    preferred_form_factor: Optional[str] = Field(default=None, description="Case or motherboard form factor requirement")
    socket: Optional[str] = Field(default=None, description="Required CPU socket, e.g. AM4, AM5, LGA1700")
    pcie_slot: Optional[str] = Field(default=None, description="PCIe requirement, e.g. PCIe 4.0 x16")
    max_gpu_length_mm: Optional[int] = Field(default=None, description="Maximum GPU clearance length in millimeters")


class UserProfile(BaseModel):
    profile_name: str = Field(default="My PC Rig", description="User PC configuration name")
    existing_components: ExistingComponents = Field(
        default_factory=ExistingComponents,
        description="User existing PC components"
    )
    intended_upgrade: Optional[IntendedUpgrade] = Field(
        default=None,
        description="Target component upgrade"
    )
    compatibility_requirements: Optional[CompatibilityRequirements] = Field(
        default=None,
        description="Specific user compatibility constraints"
    )
    max_budget_idr: Optional[int] = Field(
        default=None,
        ge=0,
        description="Optional maximum budget in Indonesian Rupiah (IDR)"
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp of last profile update"
    )
