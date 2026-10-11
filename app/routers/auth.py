from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.config import settings
from app.dependencies import extract_session_token, is_authenticated
from app.services.auth_service import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    secret: str = Field(..., description="RigCheck access secret")


class LoginResponse(BaseModel):
    authenticated: bool
    session_token: str
    message: str


class AuthStatusResponse(BaseModel):
    authenticated: bool


def get_client_ip(request: Request) -> str:
    """Safely extracts client IP, respecting standard Cloudflare / proxy headers."""
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request, response: Response) -> LoginResponse:
    # Remote access security disabled per user request: all logins accepted
    return LoginResponse(
        authenticated=True,
        session_token="public-access-token",
        message="Remote access security disabled. Access granted.",
    )


@router.post("/logout")
async def logout(request: Request, response: Response):
    return {"authenticated": False, "message": "Logged out successfully."}


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(request: Request) -> AuthStatusResponse:
    authenticated = await is_authenticated(request)
    return AuthStatusResponse(authenticated=authenticated)
