from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.config import settings
from app.dependencies import require_authenticated
from app.models.compatibility import AnalysisResponse
from app.services.compatibility import compatibility_engine
from app.services.ollama_client import ollama_client
from app.services.profile_storage import profile_storage

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze uploaded component image and check compatibility against saved profile",
)
async def analyze_component(
    file: UploadFile = File(..., description="Uploaded component label or hardware photo"),
    price_idr: Optional[int] = Form(
        None, description="Optional user-entered component price in Indonesian Rupiah"
    ),
    enable_search: bool = Form(
        True, description="Allow web search fallback for missing critical specifications"
    ),
    _token: str = Depends(require_authenticated),
) -> AnalysisResponse:
    # 1. Validate content type
    content_type = file.content_type or ""
    if content_type.lower() not in settings.allowed_image_content_types:
        allowed_str = ", ".join(settings.allowed_image_content_types)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid image type '{content_type}'. "
                f"Only {allowed_str} are supported."
            ),
        )

    # 2. Validate price if supplied
    if price_idr is not None and price_idr < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price in IDR cannot be negative.",
        )

    # 3. Read image bytes with size constraint (streaming chunks to avoid memory blowup)
    max_size = settings.max_upload_size_bytes
    chunk_size = 64 * 1024
    total_bytes = bytearray()

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_bytes.extend(chunk)
        if len(total_bytes) > max_size:
            max_mb = max_size // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uploaded image exceeds maximum allowed size of {max_mb} MB.",
            )

    if len(total_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image file is empty.",
        )

    image_bytes = bytes(total_bytes)

    # 4. Run local vision extraction pipeline through Ollama
    (
        specs,
        evidence,
        unresolved_fields,
        preliminary_status,
        search_enrichment,
    ) = await ollama_client.extract_from_image(
        image_bytes, trigger_search_if_needed=enable_search
    )

    # 5. Load current user profile from local JSON storage
    user_profile = profile_storage.get_profile()

    # 6. Evaluate compatibility rules
    compatibility_report = compatibility_engine.evaluate(
        specs=specs,
        profile=user_profile,
        user_price_idr=price_idr,
    )

    return AnalysisResponse(
        preliminary_status=preliminary_status,
        extracted_specifications=specs,
        evidence=evidence,
        unresolved_fields=unresolved_fields,
        search_enrichment=search_enrichment,
        compatibility_report=compatibility_report,
        user_price_idr=price_idr,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )
