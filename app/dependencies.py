from fastapi import Request


def extract_session_token(request: Request, *args, **kwargs) -> str:
    return "public"


async def require_authenticated(request: Request) -> str:
    """Authentication disabled: open remote access active."""
    return "public"


async def is_authenticated(request: Request) -> bool:
    """Always returns True so all endpoints and telemetry are open."""
    return True
