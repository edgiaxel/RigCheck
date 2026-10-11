from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import require_authenticated
from app.models.profile import UserProfile
from app.services.profile_storage import profile_storage

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    _token: str = Depends(require_authenticated),
) -> UserProfile:
    """Retrieve the current saved PC configuration profile (requires authentication)."""
    try:
        return profile_storage.get_profile()
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to load user profile: {str(exc)}"
        )


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserProfile,
    _token: str = Depends(require_authenticated),
) -> UserProfile:
    """Update and persist the user PC configuration profile (requires authentication)."""
    try:
        updated = profile_storage.save_profile(profile_data)
        return updated
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to persist user profile: {str(exc)}"
        )
