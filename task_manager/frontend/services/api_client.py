"""Thin HTTP client wrapping `requests`: auth header injection + error normalization.

Pages and components never call `requests` directly - they go through the
per-resource service modules in this package, which use this client.
"""

import requests
import streamlit as st

from utils.session import BACKEND_API_URL


class ApiError(Exception):
    """Raised for any non-2xx response or connection failure."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class ApiClient:
    def __init__(self, base_url: str = BACKEND_API_URL) -> None:
        self._base_url = base_url

    def get(self, path: str, params: dict | None = None):
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict | None = None):
        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict | None = None):
        return self._request("PUT", path, json=json)

    def patch(self, path: str, json: dict | None = None):
        return self._request("PATCH", path, json=json)

    def delete(self, path: str):
        return self._request("DELETE", path)

    def _headers(self) -> dict:
        token = st.session_state.get("access_token")
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _request(self, method: str, path: str, **kwargs):
        try:
            response = requests.request(
                method,
                f"{self._base_url}{path}",
                headers=self._headers(),
                timeout=10,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiError(0, "Could not reach the backend server.") from exc

        if not response.ok:
            detail = response.reason
            if response.content:
                try:
                    detail = response.json().get("detail", detail)
                except ValueError:
                    pass
            raise ApiError(response.status_code, detail)

        return response.json() if response.content else None
