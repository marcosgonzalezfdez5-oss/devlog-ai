"""Authentication endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.error import ErrorResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse, "description": "Invalid email or password"}},
    summary="Log in with email and password",
    description="Authenticates against Supabase Auth and returns an access token to use as a Bearer token on subsequent requests.",
)
def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    return auth_service.login(payload.email, payload.password)
