"""JWT verification for Supabase-issued access tokens."""

import jwt

from app.config import Settings
from app.utils.exceptions import UnauthorizedError

_ALGORITHM = "HS256"
_AUDIENCE = "authenticated"


def decode_access_token(token: str, settings: Settings) -> dict:
    """Decode and verify a Supabase access token locally.

    Validates signature, expiry, and audience without calling out to
    Supabase. Raises UnauthorizedError on any failure.
    """
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[_ALGORITHM],
            audience=_AUDIENCE,
        )
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Invalid authentication token") from exc
