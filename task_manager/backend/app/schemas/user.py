"""Response schema for listing assignable users."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: UUID
    full_name: str | None

    model_config = ConfigDict(from_attributes=True)
