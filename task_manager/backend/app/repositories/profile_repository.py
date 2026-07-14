"""Database access for the `profiles` table. No business logic lives here."""

from uuid import UUID

from supabase import Client

from app.models.profile import Profile

_TABLE = "profiles"
_COLUMNS = "id, full_name"


class ProfileRepository:
    def __init__(self, client: Client) -> None:
        self._client = client

    def list_all(self) -> list[Profile]:
        result = self._client.table(_TABLE).select(_COLUMNS).execute()
        return [Profile.model_validate(row) for row in result.data]

    def get_by_id(self, profile_id: UUID) -> Profile | None:
        result = (
            self._client.table(_TABLE)
            .select(_COLUMNS)
            .eq("id", str(profile_id))
            .maybe_single()
            .execute()
        )
        if result.data is None:
            return None
        return Profile.model_validate(result.data)
