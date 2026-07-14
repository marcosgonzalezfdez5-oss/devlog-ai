"""Application-level exception hierarchy.

Services and repositories raise these instead of leaking raw exceptions
(e.g. from supabase-py) up to the API layer. main.py registers one
exception handler per class to translate them into HTTP responses.
"""


class AppError(Exception):
    """Base class for all expected application errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Requested resource does not exist. Maps to HTTP 404."""


class ValidationError(AppError):
    """Request is well-formed but semantically invalid. Maps to HTTP 422."""


class ConflictError(AppError):
    """Request conflicts with current state. Maps to HTTP 400."""


class UnauthorizedError(AppError):
    """Missing, invalid, or expired credentials. Maps to HTTP 401."""


class ForbiddenError(AppError):
    """Caller is authenticated but not allowed to perform this action. Maps to HTTP 403."""
