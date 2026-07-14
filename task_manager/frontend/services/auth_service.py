"""API client calls for authentication."""

from services.api_client import ApiClient

_client = ApiClient()


def login(email: str, password: str) -> dict:
    """Returns {access_token, token_type, user_id, email} on success."""
    return _client.post("/login", json={"email": email, "password": password})
