"""Internal representation of a user profile."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Profile(BaseModel):
    """Internal representation of a `profiles` row."""

    id: UUID
    full_name: str | None

    model_config = ConfigDict(from_attributes=True)
