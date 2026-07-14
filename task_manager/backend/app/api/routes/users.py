"""Endpoint exposing assignable users, since the frontend never queries Supabase directly."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_profile_service
from app.schemas.user import UserResponse
from app.services.profile_service import ProfileService

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)]
)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List assignable users",
    description="Returns every user profile, used to populate the task assignee dropdown.",
)
def list_users(
    profile_service: ProfileService = Depends(get_profile_service),
) -> list[UserResponse]:
    return profile_service.list_users()
