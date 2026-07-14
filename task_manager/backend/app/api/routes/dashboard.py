"""Dashboard endpoint: status counts plus the most recently created tasks."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_dashboard_service
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)]
)


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get dashboard summary",
    description="Returns task counts by status and the 5 most recently created tasks.",
)
def get_dashboard(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    return dashboard_service.get_dashboard()
