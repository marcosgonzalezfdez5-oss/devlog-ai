"""Reads back previously generated QA reports for the API layer."""

from pathlib import Path

from app.api.schemas import ReportSummary
from app.models.reports import QAReport
from app.utils.exceptions import NotFoundError


def list_reports(reports_dir: Path) -> list[ReportSummary]:
    """Summarize every finished run under `reports_dir`, newest first.

    Run directories without a `qa_report.json` (in-progress or failed
    runs) are silently skipped rather than treated as an error.
    """
    if not reports_dir.is_dir():
        return []

    summaries: list[ReportSummary] = []
    for run_dir in reports_dir.iterdir():
        report_path = run_dir / "qa_report.json"
        if not report_path.is_file():
            continue
        report = QAReport.model_validate_json(report_path.read_text(encoding="utf-8"))
        summaries.append(
            ReportSummary(
                run_id=run_dir.name,
                generated_at=report.generated_at,
                feature_title=report.feature_summary.title,
                deployment_status=report.deployment_decision.status,
            )
        )

    return sorted(summaries, key=lambda s: s.generated_at, reverse=True)


def get_report(reports_dir: Path, run_id: str) -> QAReport:
    """Read the full `QAReport` for one run. Raises `NotFoundError` if missing."""
    report_path = reports_dir / run_id / "qa_report.json"
    if not report_path.is_file():
        raise NotFoundError(f"No finished report found for run_id={run_id!r}.")
    return QAReport.model_validate_json(report_path.read_text(encoding="utf-8"))
