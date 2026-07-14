"""JWT verification for Supabase-issued access tokens."""

from functools import lru_cache

import jwt

from app.config import Settings
from app.utils.exceptions import UnauthorizedError

_ALGORITHMS = ["ES256"]
_AUDIENCE = "authenticated"


@lru_cache
def _get_jwk_client(supabase_url: str) -> jwt.PyJWKClient:
    """Cached JWKS client for a given Supabase project (fetches/caches signing keys)."""
    return jwt.PyJWKClient(f"{supabase_url}/auth/v1/.well-known/jwks.json")


def decode_access_token(token: str, settings: Settings) -> dict:
    """Decode and verify a Supabase access token against the project's JWKS.

    Supabase signs tokens with its ECC P-256 (ES256) signing key; the
    matching public key is fetched from the project's JWKS endpoint by
    `kid`. Validates signature, expiry, and audience. Raises
    UnauthorizedError on any failure.
    """
    try:
        jwk_client = _get_jwk_client(settings.supabase_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=_ALGORITHMS,
            audience=_AUDIENCE,
        )
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid authentication token") from exc
