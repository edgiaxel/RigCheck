import base64
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from pydantic import ValidationError

from app.config import settings
from app.models.analysis import (
    ExtractedSpecifications,
    PreliminaryAnalysisStatus,
    RawVisionExtraction,
    SearchEnrichment,
    VisionExtractionEvidence,
)
from app.services.search_service import SearchService, search_service

logger = logging.getLogger(__name__)


VISION_PROMPT = """You are a rigorous PC hardware vision analyzer for RigCheck.
Analyze the provided image of a PC hardware component, box, label, or serial sticker.

CRITICAL RULES:
1. ONLY extract information that is EXPLICITLY visible on the label or component.
2. DO NOT GUESS OR ESTIMATE. If a specification (such as wattage, socket, or dimensions) is not legibly printed on the image, set it to null. Never assume or extrapolate specifications.
3. Preserve uncertainty: If text is blurry or ambiguous, note it in confidence_notes.
4. If this is not a PC component, set preliminary_status to "INSUFFICIENT_DATA".
5. List any specifications that cannot be confirmed from the visual label alone in "unresolved_fields".

Respond ONLY with a valid JSON object with the following fields:
{
  "category": "GPU" | "CPU" | "Motherboard" | "PSU" | "RAM" | "Storage" | "Cooler" | "Case" | null,
  "brand": string | null,
  "model": string | null,
  "series_or_chipset": string | null,
  "power_tdp_watts": integer | null,
  "recommended_psu_watts": integer | null,
  "socket": string | null,
  "form_factor": string | null,
  "memory_spec": string | null,
  "interface_or_slot": string | null,
  "dimensions_or_clearance": string | null,
  "power_connectors": string | null,
  "part_or_model_number": string | null,
  "visible_labels": [string],
  "confidence_notes": string | null,
  "unresolved_fields": [string],
  "preliminary_status": "EXTRACTED" | "PARTIALLY_IDENTIFIED" | "UNCERTAIN" | "INSUFFICIENT_DATA"
}
"""

ENRICHMENT_PROMPT_TEMPLATE = """You are a technical PC hardware evaluator.
Review the following web search snippets for the component: {brand} {model}.

Search snippets:
{snippets}

Based ONLY on these search snippets, extract any of the following missing specifications if mentioned with certainty:
- power_tdp_watts: integer or null
- recommended_psu_watts: integer or null
- socket: string or null
- form_factor: string or null
- memory_spec: string or null
- interface_or_slot: string or null

Respond ONLY with a valid JSON object containing those keys. Do not guess if not supported by the snippets.
"""


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Safely extracts JSON from model response, handling code blocks and prefix/suffix text."""
    if not text or not text.strip():
        raise ValueError("Empty response received from model.")

    cleaned = text.strip()

    # Remove markdown code fences if present
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if code_block_match:
        cleaned = code_block_match.group(1).strip()

    # Find matching outermost braces if extra narrative exists
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]

    return json.loads(cleaned)


class OllamaVisionClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        search_svc: Optional[SearchService] = None,
    ):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout if timeout is not None else settings.ollama_timeout_seconds
        self.search_service = search_svc or search_service

    async def check_health(self) -> Dict[str, Any]:
        """Check Ollama connectivity and verify loaded models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    has_model = any(self.model in m for m in models)
                    return {
                        "available": True,
                        "model_present": has_model,
                        "configured_model": self.model,
                        "installed_models": models,
                    }
                return {
                    "available": False,
                    "status_code": res.status_code,
                    "model_present": False,
                    "configured_model": self.model,
                }
        except Exception as exc:
            return {
                "available": False,
                "error": str(exc),
                "model_present": False,
                "configured_model": self.model,
            }

    async def extract_from_image(
        self, image_bytes: bytes, trigger_search_if_needed: bool = True
    ) -> Tuple[
        ExtractedSpecifications,
        VisionExtractionEvidence,
        List[str],
        PreliminaryAnalysisStatus,
        Optional[SearchEnrichment],
    ]:
        """Run vision extraction pipeline on image bytes, optionally enriching via search."""
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": self.model,
            "prompt": VISION_PROMPT,
            "images": [b64_image],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)

            if resp.status_code != 200:
                raise RuntimeError(
                    f"Ollama returned HTTP {resp.status_code}: {resp.text[:300]}"
                )

            data = resp.json()
            raw_text = data.get("response", "")
            parsed_json = extract_json_from_text(raw_text)

        except (httpx.RequestError, RuntimeError) as exc:
            logger.error(f"Ollama request failure: {exc}")
            # Safe fallback returning uncertain extraction rather than crashing
            evidence = VisionExtractionEvidence(
                visible_labels=[],
                confidence_notes=f"Vision model communication error: {str(exc)}",
            )
            return (
                ExtractedSpecifications(),
                evidence,
                ["all_fields"],
                PreliminaryAnalysisStatus.UNCERTAIN,
                None,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning(f"Failed to parse JSON from vision model: {exc}")
            evidence = VisionExtractionEvidence(
                visible_labels=[],
                confidence_notes="Model generated non-JSON response.",
            )
            return (
                ExtractedSpecifications(),
                evidence,
                ["all_fields"],
                PreliminaryAnalysisStatus.UNCERTAIN,
                None,
            )

        # Validate with Pydantic
        try:
            raw_data = RawVisionExtraction.model_validate(parsed_json)
        except ValidationError as exc:
            logger.warning(f"Vision output validation error: {exc}")
            raw_data = RawVisionExtraction()

        specs = ExtractedSpecifications(
            category=raw_data.category,
            brand=raw_data.brand,
            model=raw_data.model,
            series_or_chipset=raw_data.series_or_chipset,
            power_tdp_watts=raw_data.power_tdp_watts,
            recommended_psu_watts=raw_data.recommended_psu_watts,
            socket=raw_data.socket,
            form_factor=raw_data.form_factor,
            memory_spec=raw_data.memory_spec,
            interface_or_slot=raw_data.interface_or_slot,
            dimensions_or_clearance=raw_data.dimensions_or_clearance,
            power_connectors=raw_data.power_connectors,
            other_visible_specs=raw_data.other_visible_specs,
        )

        evidence = VisionExtractionEvidence(
            visible_labels=raw_data.visible_labels,
            part_or_model_number=raw_data.part_or_model_number,
            confidence_notes=raw_data.confidence_notes,
        )

        unresolved = list(raw_data.unresolved_fields)

        # Audit missing critical fields to ensure uncertainty is preserved
        self._audit_unresolved_fields(specs, unresolved)

        # Determine preliminary status
        preliminary_status = self._evaluate_status(specs, raw_data.preliminary_status)

        # Online search enrichment if specs are missing and component is identified
        search_enrichment: Optional[SearchEnrichment] = None
        if trigger_search_if_needed and self._needs_technical_search(specs):
            search_enrichment = await self._perform_search_enrichment(specs, unresolved)

        return specs, evidence, unresolved, preliminary_status, search_enrichment

    def _audit_unresolved_fields(
        self, specs: ExtractedSpecifications, unresolved: List[str]
    ) -> None:
        """Ensure missing fields are explicitly recorded in unresolved_fields."""
        critical_fields = [
            ("category", specs.category),
            ("brand", specs.brand),
            ("model", specs.model),
            ("power_tdp_watts", specs.power_tdp_watts),
            ("recommended_psu_watts", specs.recommended_psu_watts),
        ]
        if specs.category in ("CPU", "Motherboard"):
            critical_fields.append(("socket", specs.socket))
        if specs.category in ("Motherboard", "Case", "PSU"):
            critical_fields.append(("form_factor", specs.form_factor))

        for name, val in critical_fields:
            if val is None and name not in unresolved:
                unresolved.append(name)

    def _evaluate_status(
        self, specs: ExtractedSpecifications, model_suggested: Optional[str]
    ) -> PreliminaryAnalysisStatus:
        if not specs.category and not specs.brand and not specs.model:
            return PreliminaryAnalysisStatus.INSUFFICIENT_DATA
        if specs.brand and specs.model and specs.category:
            return PreliminaryAnalysisStatus.EXTRACTED
        if specs.brand or specs.model or specs.category:
            return PreliminaryAnalysisStatus.PARTIALLY_IDENTIFIED
        return PreliminaryAnalysisStatus.UNCERTAIN

    def _needs_technical_search(self, specs: ExtractedSpecifications) -> bool:
        """Determine if search is warranted (identified component missing critical specs)."""
        if not (specs.brand and specs.model):
            return False
        # If GPU missing recommended_psu or tdp
        if specs.category == "GPU" and (
            specs.recommended_psu_watts is None or specs.power_tdp_watts is None
        ):
            return True
        # If CPU missing TDP or socket
        if specs.category == "CPU" and (
            specs.power_tdp_watts is None or specs.socket is None
        ):
            return True
        return False

    async def _perform_search_enrichment(
        self, specs: ExtractedSpecifications, unresolved: List[str]
    ) -> Optional[SearchEnrichment]:
        category_term = ""
        if specs.category == "GPU":
            category_term = "graphics card GPU"
        elif specs.category == "CPU":
            category_term = "processor CPU socket"
        elif specs.category:
            category_term = specs.category

        query_parts = [p for p in [specs.brand, specs.model, category_term, "specifications TDP recommended PSU"] if p]
        query = " ".join(query_parts)
        search_result = await self.search_service.search_technical_specs(query, max_results=3)

        if not search_result or not search_result.get("results"):
            return None

        snippets_text = "\n\n".join(
            f"[{r.get('title', '')}]: {r.get('snippet', '')}"
            for r in search_result["results"]
        )
        sources = [
            f"{r.get('title', '')} ({r.get('link', '')})"
            for r in search_result["results"]
            if r.get("link")
        ]

        # Use Gemma to parse search snippets
        prompt = ENRICHMENT_PROMPT_TEMPLATE.format(
            brand=specs.brand,
            model=specs.model,
            snippets=snippets_text,
        )

        resolved_fields: List[str] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "format": "json",
                        "stream": False,
                        "options": {"temperature": 0.0},
                    },
                )

            if res.status_code == 200:
                enrich_json = extract_json_from_text(res.json().get("response", ""))

                # Apply enriched values if found
                if enrich_json.get("power_tdp_watts") and specs.power_tdp_watts is None:
                    try:
                        specs.power_tdp_watts = int(enrich_json["power_tdp_watts"])
                        resolved_fields.append("power_tdp_watts")
                        if "power_tdp_watts" in unresolved:
                            unresolved.remove("power_tdp_watts")
                    except (ValueError, TypeError):
                        pass

                if (
                    enrich_json.get("recommended_psu_watts")
                    and specs.recommended_psu_watts is None
                ):
                    try:
                        specs.recommended_psu_watts = int(enrich_json["recommended_psu_watts"])
                        resolved_fields.append("recommended_psu_watts")
                        if "recommended_psu_watts" in unresolved:
                            unresolved.remove("recommended_psu_watts")
                    except (ValueError, TypeError):
                        pass

                if enrich_json.get("socket") and specs.socket is None:
                    specs.socket = str(enrich_json["socket"]).strip()
                    resolved_fields.append("socket")
                    if "socket" in unresolved:
                        unresolved.remove("socket")

                if enrich_json.get("form_factor") and specs.form_factor is None:
                    specs.form_factor = str(enrich_json["form_factor"]).strip()
                    resolved_fields.append("form_factor")
                    if "form_factor" in unresolved:
                        unresolved.remove("form_factor")

        except Exception as exc:
            logger.warning(f"Error enriching specifications via model: {exc}")

        return SearchEnrichment(
            performed=True,
            query=query,
            sources=sources,
            resolved_fields=resolved_fields,
            search_summary=(
                f"Resolved {len(resolved_fields)} specifications online"
                if resolved_fields
                else "Searched online references but no definitive specs could be verified."
            ),
        )


ollama_client = OllamaVisionClient()
