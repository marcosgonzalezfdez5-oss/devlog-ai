from datetime import UTC, datetime
from pathlib import Path

from app.models.enums import CoverageStatus, DeploymentDecisionStatus
from app.models.reports import DeploymentDecision, QAReport
from app.models.state import ChangedFiles, CoverageReport, DocumentationStatus, FeatureSummary, TestResults
from app.services.reporting_service import render_markdown, write_report


def _report(status: DeploymentDecisionStatus = DeploymentDecisionStatus.READY) -> QAReport:
    return QAReport(
        feature_summary=FeatureSummary(title="Task editing", description="Adds validation.", affected_areas=["Task Management"]),
        changed_files=ChangedFiles(base_ref="main", target_ref="abc123", files=[], affected_modules=["Task Management"]),
        coverage_report=CoverageReport(
            unit=CoverageStatus.PRESENT,
            integration=CoverageStatus.PRESENT,
            e2e=CoverageStatus.NOT_REQUIRED,
            performance=CoverageStatus.NOT_REQUIRED,
            found_test_files=[],
        ),
        test_results=TestResults(),
        failure_analysis=None,
        documentation_status=DocumentationStatus(updated=True, updated_files=["README.md"], skipped_reason=None),
        deployment_decision=DeploymentDecision(status=status, reason="All good", blocking_issues=[]),
        generated_at=datetime.now(UTC),
    )


def test_render_markdown_includes_key_sections():
    markdown = render_markdown(_report())

    assert "# QA Report" in markdown
    assert "Task editing" in markdown
    assert "READY" in markdown
    assert "Updated" in markdown


def test_write_report_persists_markdown_and_json(tmp_path: Path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    markdown_path = write_report(run_dir, _report())

    assert markdown_path == run_dir / "qa_report.md"
    assert markdown_path.exists()
    assert (run_dir / "qa_report.json").exists()

    reloaded = QAReport.model_validate_json((run_dir / "qa_report.json").read_text(encoding="utf-8"))
    assert reloaded.feature_summary.title == "Task editing"
