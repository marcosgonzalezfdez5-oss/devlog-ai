"""Application-level exception hierarchy.

Services raise these instead of leaking raw exceptions up to the API
layer. main.py registers one exception handler per class to translate
them into HTTP responses.
"""


class AppError(Exception):
    """Base class for all expected application errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Requested resource does not exist. Maps to HTTP 404."""


class AgentExecutionError(AppError):
    """The Deep Agent run itself failed. Maps to HTTP 502."""
