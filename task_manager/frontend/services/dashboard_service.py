"""API client call for the dashboard summary."""

from services.api_client import ApiClient

_client = ApiClient()


def get_dashboard() -> dict:
    """Returns {stats: {...}, recent_tasks: [...]}."""
    return _client.get("/dashboard")
