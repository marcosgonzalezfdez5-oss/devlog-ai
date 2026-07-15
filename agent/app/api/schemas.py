"""Request/response schemas for the FastAPI layer.

Reuses the Phase 2 domain models (`app/models/`) as fields rather than
re-declaring their shape here.
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DeploymentDecisionStatus
from app.models.state import ChangedFiles, CoverageReport


class HealthResponse(BaseModel):
    status: str = "ok"


class AnalyzeRequest(BaseModel):
    base_ref: str = "main"


class AnalyzeResponse(BaseModel):
    changed_files: ChangedFiles
    coverage_report: CoverageReport


class RunRequest(BaseModel):
    feature_request: str
    base_ref: str = "main"
    run_id: str | None = None


class RunResponse(BaseModel):
    run_id: str
    message: str
    deployment_status: DeploymentDecisionStatus


class ReportSummary(BaseModel):
    run_id: str
    generated_at: datetime
    feature_title: str
    deployment_status: DeploymentDecisionStatus


class ReportListResponse(BaseModel):
    reports: list[ReportSummary]


class ErrorResponse(BaseModel):
    detail: str
