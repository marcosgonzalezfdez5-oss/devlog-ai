"""Internal representation of an authenticated caller."""

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """The identity decoded from a verified Supabase access token."""

    id: str
    email: str | None = None
