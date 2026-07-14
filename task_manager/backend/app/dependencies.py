"""FastAPI dependency providers.

Wires the DI chain: settings -> supabase clients -> repositories ->
services -> route handlers, plus the `get_current_user` auth guard.
"""

from functools import lru_cache

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

from app.config import Settings, get_settings
from app.models.auth import AuthenticatedUser
from app.repositories.profile_repository import ProfileRepository
from app.repositories.task_repository import TaskRepository
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.profile_service import ProfileService
from app.services.task_service import TaskService
from app.utils.exceptions import UnauthorizedError
from app.utils.security import decode_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_supabase_anon_client() -> Client:
    """Supabase client scoped to the anon key, used only for auth.sign_in."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_auth_service(anon_client: Client = Depends(get_supabase_anon_client)) -> AuthService:
    return AuthService(anon_client)


@lru_cache
def get_supabase_service_client() -> Client:
    """Supabase client scoped to the service-role key.

    Used by repositories to read/write tasks and profiles, bypassing RLS -
    the backend itself is the trusted access point and enforces its own
    authorization rules in the service layer.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def get_task_repository(
    client: Client = Depends(get_supabase_service_client),
) -> TaskRepository:
    return TaskRepository(client)


def get_profile_repository(
    client: Client = Depends(get_supabase_service_client),
) -> ProfileRepository:
    return ProfileRepository(client)


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
) -> TaskService:
    return TaskService(task_repo, profile_repo)


def get_dashboard_service(
    task_repo: TaskRepository = Depends(get_task_repository),
) -> DashboardService:
    return DashboardService(task_repo)


def get_profile_service(
    profile_repo: ProfileRepository = Depends(get_profile_repository),
) -> ProfileService:
    return ProfileService(profile_repo)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> AuthenticatedUser:
    """Resolve the authenticated caller from the `Authorization: Bearer` header."""
    if credentials is None:
        raise UnauthorizedError("Missing authentication token")

    payload = decode_access_token(credentials.credentials, settings)
    return AuthenticatedUser(id=payload["sub"], email=payload.get("email"))
