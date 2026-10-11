from typing import Optional
from fastapi import Cookie, Header, HTTPException, Request, status

from app.services.auth_service import auth_service


def extract_session_token(
    request: Request,
    rigcheck_session: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    x_rigcheck_token: Optional[str] = Header(None),
) -> Optional[str]:
    """Extracts session token from Cookie, Authorization header, or X-RigCheck-Token header."""
    # 1. Check Cookie
    if rigcheck_session and rigcheck_session.strip():
        return rigcheck_session.strip()

    # 2. Check X-RigCheck-Token Header
    if x_rigcheck_token and x_rigcheck_token.strip():
        return x_rigcheck_token.strip()

    # 3. Check Authorization Bearer Header
    if authorization and authorization.strip():
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]

    return None


async def require_authenticated(
    request: Request,
    token: Optional[str] = Cookie(None, alias="rigcheck_session"),
) -> str:
    """Enforces active authenticated session. Raises HTTP 401 if missing or invalid."""
    extracted = extract_session_token(
        request=request,
        rigcheck_session=request.cookies.get("rigcheck_session"),
        authorization=request.headers.get("authorization"),
        x_rigcheck_token=request.headers.get("x-rigcheck-token"),
    )

    if not extracted or not auth_service.is_session_valid(extracted):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please enter your RigCheck access secret.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return extracted


async def is_authenticated(request: Request) -> bool:
    """Non-blocking check returning True if the caller is currently authenticated."""
    extracted = extract_session_token(
        request=request,
        rigcheck_session=request.cookies.get("rigcheck_session"),
        authorization=request.headers.get("authorization"),
        x_rigcheck_token=request.headers.get("x-rigcheck-token"),
    )
    return bool(extracted and auth_service.is_session_valid(extracted))
