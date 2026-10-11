from typing import Any, Dict
from fastapi import APIRouter, Request

from app.config import settings
from app.dependencies import is_authenticated
from app.services.ollama_client import ollama_client
from app.services.profile_storage import profile_storage

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Health check endpoint. Returns detailed telemetry only to authenticated callers."""
    authenticated = await is_authenticated(request)

    if not authenticated:
        return {
            "status": "online",
            "service": "RigCheck Backend",
            "version": "0.2.0",
            "authenticated": False,
        }

    ollama_status = await ollama_client.check_health()
    profile = profile_storage.get_profile()

    return {
        "status": "healthy" if ollama_status.get("available") else "degraded",
        "service": "RigCheck Backend",
        "version": "0.2.0",
        "authenticated": True,
        "ollama": ollama_status,
        "search_service": {
            "enabled": settings.serpapi_enabled,
            "configured": bool(settings.serpapi_api_key),
        },
        "storage": {
            "profile_loaded": bool(profile.profile_name),
        },
    }
