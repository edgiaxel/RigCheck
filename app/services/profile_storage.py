import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.profile import UserProfile


class ProfileStorageService:
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or settings.profile_storage_path)

    def _ensure_directory(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def get_profile(self) -> UserProfile:
        """Load user profile from JSON file or return a clean default if not yet created."""
        if not self.storage_path.exists():
            return UserProfile()

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserProfile.model_validate(data)
        except (json.JSONDecodeError, ValueError) as err:
            # If the profile JSON is corrupted, do not crash the app, provide a clean default
            # while logging/preserving error context
            return UserProfile(profile_name="My PC Rig (Recovered Default)")

    def save_profile(self, profile: UserProfile) -> UserProfile:
        """Atomically persist user profile to local JSON storage."""
        self._ensure_directory()

        # Update timestamp
        profile.updated_at = datetime.now(timezone.utc).isoformat()
        serialized = profile.model_dump(mode="json")

        temp_path = self.storage_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.storage_path)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

        return profile


profile_storage = ProfileStorageService()
