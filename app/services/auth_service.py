import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        # Maps session_token -> expiration datetime (UTC)
        self._active_sessions: Dict[str, datetime] = {}
        # Maps client_ip -> (failure_count, lockout_until_datetime)
        self._failed_attempts: Dict[str, Tuple[int, Optional[datetime]]] = {}

    def get_configured_secret(self) -> str:
        return settings.get_effective_access_secret()

    def check_rate_limit(self, client_ip: str) -> Tuple[bool, int]:
        """Checks if client IP is currently rate-limited due to repeated failures.
        
        Returns (is_blocked, remaining_seconds).
        """
        now = datetime.now(timezone.utc)
        record = self._failed_attempts.get(client_ip)
        if not record:
            return False, 0

        count, lockout_until = record
        if lockout_until and now < lockout_until:
            remaining = int((lockout_until - now).total_seconds())
            return True, max(1, remaining)

        # Clear expired lockout
        if lockout_until and now >= lockout_until:
            self._failed_attempts.pop(client_ip, None)

        return False, 0

    def record_failure(self, client_ip: str) -> None:
        """Records a failed authentication attempt and applies lockout if threshold exceeded."""
        now = datetime.now(timezone.utc)
        record = self._failed_attempts.get(client_ip)
        count = (record[0] + 1) if record else 1

        if count >= settings.max_failed_auth_attempts:
            lockout_until = now + timedelta(seconds=settings.auth_lockout_seconds)
            self._failed_attempts[client_ip] = (count, lockout_until)
            logger.warning(
                f"Rate limit triggered for IP {client_ip} after {count} failed attempts. "
                f"Locked out for {settings.auth_lockout_seconds}s."
            )
        else:
            self._failed_attempts[client_ip] = (count, None)

    def record_success(self, client_ip: str) -> None:
        """Clears failed attempts counter upon successful verification."""
        self._failed_attempts.pop(client_ip, None)

    def verify_secret(self, candidate_secret: str, client_ip: str = "unknown") -> bool:
        """Verifies candidate secret using constant-time comparison."""
        is_blocked, _ = self.check_rate_limit(client_ip)
        if is_blocked:
            return False

        effective_secret = self.get_configured_secret()
        candidate = candidate_secret.strip() if candidate_secret else ""
        match = secrets.compare_digest(candidate, effective_secret)

        if match:
            self.record_success(client_ip)
        else:
            self.record_failure(client_ip)

        return match

    def create_session(self) -> str:
        """Generates a secure random session token valid for session_ttl_hours."""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.session_ttl_hours)
        self._active_sessions[session_token] = expires_at
        return session_token

    def is_session_valid(self, session_token: Optional[str]) -> bool:
        """Validates that a session token exists and has not expired."""
        if not session_token:
            return False

        now = datetime.now(timezone.utc)
        expires_at = self._active_sessions.get(session_token)
        if not expires_at:
            return False

        if now > expires_at:
            # Expired session
            self._active_sessions.pop(session_token, None)
            return False

        return True

    def revoke_session(self, session_token: Optional[str]) -> None:
        """Revokes an active session."""
        if session_token:
            self._active_sessions.pop(session_token, None)


auth_service = AuthService()
