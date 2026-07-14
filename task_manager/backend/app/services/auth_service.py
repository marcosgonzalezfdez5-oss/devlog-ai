"""Business logic for authenticating users against Supabase Auth."""

from gotrue.errors import AuthApiError
from supabase import Client

from app.schemas.auth import LoginResponse
from app.utils.exceptions import UnauthorizedError


class AuthService:
    """Handles login against Supabase Auth via an anon-key client."""

    def __init__(self, anon_client: Client) -> None:
        self._anon_client = anon_client

    def login(self, email: str, password: str) -> LoginResponse:
        """Authenticate a user and return an access token for API calls."""
        try:
            result = self._anon_client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
        except AuthApiError as exc:
            raise UnauthorizedError("Invalid email or password") from exc

        return LoginResponse(
            access_token=result.session.access_token,
            user_id=result.user.id,
            email=result.user.email,
        )
