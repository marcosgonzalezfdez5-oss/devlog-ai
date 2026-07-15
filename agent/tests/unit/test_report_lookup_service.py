from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.models.enums import CoverageStatus, DeploymentDecisionStatus
from app.models.reports import DeploymentDecision, QAReport
from app.models.state import ChangedFiles, CoverageReport, DocumentationStatus, FeatureSummary, TestResults
from app.services.report_lookup_service import get_report, list_reports
from app.utils.exceptions import NotFoundError


def _write_report(reports_dir: Path, run_id: str, title: str, generated_at: datetime) -> None:
    run_dir = reports_dir / run_id
    run_dir.mkdir(parents=True)
    report = QAReport(
        feature_summary=FeatureSummary(title=title, description="d", affected_areas=[]),
        changed_files=ChangedFiles(base_ref="main", target_ref="abc", files=[], affected_modules=[]),
        coverage_report=CoverageReport(
            unit=CoverageStatus.NOT_REQUIRED,
            integration=CoverageStatus.NOT_REQUIRED,
            e2e=CoverageStatus.NOT_REQUIRED,
            performance=CoverageStatus.NOT_REQUIRED,
            found_test_files=[],
        ),
        test_results=TestResults(),
        failure_analysis=None,
        documentation_status=DocumentationStatus(updated=False, updated_files=[], skipped_reason=None),
        deployment_decision=DeploymentDecision(status=DeploymentDecisionStatus.READY, reason="ok", blocking_issues=[]),
        generated_at=generated_at,
    )
    (run_dir / "qa_report.json").write_text(report.model_dump_json(), encoding="utf-8")


def test_list_reports_returns_empty_for_missing_dir(tmp_path: Path):
    assert list_reports(tmp_path / "does-not-exist") == []


def test_list_reports_skips_unfinished_runs(tmp_path: Path):
    reports_dir = tmp_path / "reports"
    (reports_dir / "in-progress-run").mkdir(parents=True)

    assert list_reports(reports_dir) == []


def test_list_reports_sorts_newest_first(tmp_path: Path):
    reports_dir = tmp_path / "reports"
    _write_report(reports_dir, "run-a", "Older", datetime(2026, 1, 1, tzinfo=UTC))
    _write_report(reports_dir, "run-b", "Newer", datetime(2026, 6, 1, tzinfo=UTC))

    summaries = list_reports(reports_dir)

    assert [s.feature_title for s in summaries] == ["Newer", "Older"]


def test_get_report_raises_not_found(tmp_path: Path):
    with pytest.raises(NotFoundError):
        get_report(tmp_path / "reports", "no-such-run")


def test_get_report_returns_full_report(tmp_path: Path):
    reports_dir = tmp_path / "reports"
    _write_report(reports_dir, "run-a", "Task editing", datetime(2026, 1, 1, tzinfo=UTC))

    report = get_report(reports_dir, "run-a")

    assert report.feature_summary.title == "Task editing"
