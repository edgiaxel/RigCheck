import secrets
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

    # Security & Remote Access Authentication
    access_secret: str = ""
    session_ttl_hours: int = 24
    max_failed_auth_attempts: int = 5
    auth_lockout_seconds: int = 30

    # Ollama vision configuration
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma3:4b"
    ollama_timeout_seconds: float = 60.0

    # SerpAPI technical search configuration
    serpapi_api_key: str = ""
    serpapi_enabled: bool = True
    serpapi_timeout_seconds: float = 10.0

    # Local persistence & upload constraints
    profile_storage_path: str = "data/user_profile.json"
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB limit
    allowed_image_content_types: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    def get_effective_access_secret(self) -> str:
        """Returns the configured access secret, or generates a strong ephemeral secret."""
        if self.access_secret and len(self.access_secret.strip()) >= 12:
            return self.access_secret.strip()
        # Ephemeral fallback generated once per process lifecycle if not set in .env
        if not hasattr(self, "_ephemeral_secret"):
            self._ephemeral_secret = secrets.token_urlsafe(32)
        return self._ephemeral_secret


settings = Settings()
