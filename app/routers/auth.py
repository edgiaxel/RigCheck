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
    client_ip = get_client_ip(request)

    # 1. Check rate limit
    is_blocked, remaining_secs = auth_service.check_rate_limit(client_ip)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please wait {remaining_secs} seconds before trying again.",
        )

    # 2. Verify secret
    is_valid = auth_service.verify_secret(payload.secret, client_ip=client_ip)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access secret. Authentication failed.",
        )

    # 3. Create active session token
    session_token = auth_service.create_session()

    # 4. Set HttpOnly Cookie (samesite='none' for cross-site Render tunnel support over HTTPS)
    is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    response.set_cookie(
        key="rigcheck_session",
        value=session_token,
        max_age=settings.session_ttl_hours * 3600,
        httponly=True,
        samesite="none" if is_https else "lax",
        secure=is_https,
        path="/",
    )

    return LoginResponse(
        authenticated=True,
        session_token=session_token,
        message="Authentication successful. Session established.",
    )


@router.post("/logout")
async def logout(request: Request, response: Response):
    token = extract_session_token(
        request=request,
        rigcheck_session=request.cookies.get("rigcheck_session"),
        authorization=request.headers.get("authorization"),
        x_rigcheck_token=request.headers.get("x-rigcheck-token"),
    )
    if token:
        auth_service.revoke_session(token)

    is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    response.delete_cookie(
        key="rigcheck_session",
        path="/",
        samesite="none" if is_https else "lax",
        secure=is_https,
    )
    return {"authenticated": False, "message": "Logged out successfully."}


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(request: Request) -> AuthStatusResponse:
    authenticated = await is_authenticated(request)
    return AuthStatusResponse(authenticated=authenticated)
