import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import analyze_router, auth_router, health_router, profile_router

logger = logging.getLogger("rigcheck.security")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Security startup notice
    configured_secret = settings.access_secret
    if configured_secret and len(configured_secret.strip()) >= 12:
        logger.info("[RigCheck Security] Access control active with secret from .env.")
    else:
        ephemeral = settings.get_effective_access_secret()
        logger.warning(
            "\n" + "=" * 70 + "\n"
            "[RigCheck Security] No ACCESS_SECRET found in .env (or too short).\n"
            f"[RigCheck Security] Generated Ephemeral Access Secret: {ephemeral}\n"
            "[RigCheck Security] Use this secret on your phone to unlock RigCheck.\n"
            + "=" * 70
        )
    yield


app = FastAPI(
    title="RigCheck API",
    description="Privacy-focused PC component compatibility assistant powered by local Ollama vision inference.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Enforces essential web security headers on all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(self)"
    return response


# Permissive CORS allowing cross-origin requests from Render and mobile browsers
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(profile_router)
app.include_router(analyze_router)

# Serve built frontend from same origin if frontend/dist is present
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
