from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.profile import router as profile_router
from app.routers.analyze import router as analyze_router

__all__ = ["auth_router", "health_router", "profile_router", "analyze_router"]
