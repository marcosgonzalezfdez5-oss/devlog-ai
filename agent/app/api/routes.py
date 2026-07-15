"""HTTP routes for the AI QA Deep Agent."""

import logging

from fastapi import APIRouter

from app.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    ReportListResponse,
    RunRequest,
    RunResponse,
)
from app.config import get_settings
from app.models.reports import DeploymentDecision, QAReport
from app.services import report_lookup_service
from app.services.coverage_service import analyze_coverage
from app.services.git_service import analyze_changes
from app.services.qa_orchestrator import run_qa_validation
from app.utils.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
def health() -> HealthResponse:
    return HealthResponse()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Preview what a full run would validate",
    description="Runs only the Git and Coverage tools directly - no LLM call, no tests executed.",
)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    settings = get_settings()
    changed_files = analyze_changes(settings.sut_repo_path, base_ref=payload.base_ref)
    coverage_report = analyze_coverage(settings.sut_repo_path, changed_files)
    return AnalyzeResponse(changed_files=changed_files, coverage_report=coverage_report)


@router.post(
    "/run",
    response_model=RunResponse,
    summary="Run a full QA validation",
    description="Invokes the Deep Agent end-to-end. Blocks until the run finishes.",
)
def run(payload: RunRequest) -> RunResponse:
    try:
        message, run_id = run_qa_validation(
            payload.feature_request, base_ref=payload.base_ref, run_id=payload.run_id
        )
    except Exception as exc:
        logger.exception("QA agent run failed for run_id=%r", payload.run_id)
        raise AgentExecutionError(f"QA agent run failed: {exc}") from exc

    decision = DeploymentDecision.model_validate_json(
        (get_settings().reports_dir / run_id / "deployment_decision.json").read_text(encoding="utf-8")
    )
    return RunResponse(run_id=run_id, message=message, deployment_status=decision.status)


@router.get("/reports", response_model=ReportListResponse, summary="List finished QA runs")
def list_reports() -> ReportListResponse:
    return ReportListResponse(reports=report_lookup_service.list_reports(get_settings().reports_dir))


@router.get("/reports/{run_id}", response_model=QAReport, summary="Get one QA run's full report")
def get_report(run_id: str) -> QAReport:
    return report_lookup_service.get_report(get_settings().reports_dir, run_id)
