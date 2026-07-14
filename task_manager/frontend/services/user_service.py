"""API client call for listing assignable users."""

from services.api_client import ApiClient

_client = ApiClient()


def list_users() -> list[dict]:
    """Returns [{id, full_name}, ...]."""
    return _client.get("/users")
