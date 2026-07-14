"""Shared error response schema, used in OpenAPI `responses=` documentation."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
