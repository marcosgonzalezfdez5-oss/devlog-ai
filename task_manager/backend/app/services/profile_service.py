"""Business logic for listing assignable users (profiles)."""

from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository


class ProfileService:
    def __init__(self, profile_repo: ProfileRepository) -> None:
        self._profile_repo = profile_repo

    def list_users(self) -> list[Profile]:
        return self._profile_repo.list_all()
