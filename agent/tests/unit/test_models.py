from datetime import UTC, datetime

from app.models.enums import CoverageStatus, DeploymentDecisionStatus, Severity, TestCategory
from app.models.reports import DeploymentDecision, QAReport
from app.models.state import (
    ChangedFiles,
    CoverageReport,
    DocumentationStatus,
    FeatureSummary,
    FileChange,
    TestCaseResult,
    TestResults,
    TestSuiteResult,
)


def _changed_files() -> ChangedFiles:
    return ChangedFiles(
        base_ref="main",
        target_ref="abc123",
        files=[FileChange(path="backend/app/api/routes/tasks.py", change_type="modified")],
        affected_modules=["Task Management"],
    )


def _coverage_report() -> CoverageReport:
    return CoverageReport(
        unit=CoverageStatus.PRESENT,
        integration=CoverageStatus.PRESENT,
        e2e=CoverageStatus.NOT_REQUIRED,
        performance=CoverageStatus.NOT_REQUIRED,
        found_test_files=["backend/tests/unit/test_tasks.py"],
    )


def test_changed_files_round_trips_through_json():
    cf = _changed_files()
    assert ChangedFiles.model_validate_json(cf.model_dump_json()) == cf


def test_all_required_passed_true_when_nothing_ran():
    assert TestResults().all_required_passed is True


def test_all_required_passed_false_when_a_suite_has_failures():
    suite = TestSuiteResult(
        category=TestCategory.UNIT,
        executed=True,
        passed=1,
        failed=1,
        skipped=0,
        duration_seconds=0.1,
        cases=[TestCaseResult(name="test_x", outcome="failed", duration_seconds=0.1, failure_message="boom")],
    )
    assert TestResults(unit=suite).all_required_passed is False


def test_all_required_passed_true_when_only_performance_present():
    results = TestResults(performance=None)
    assert results.all_required_passed is True


def test_qa_report_constructs_with_all_nested_models():
    report = QAReport(
        feature_summary=FeatureSummary(title="t", description="d", affected_areas=["Task Management"]),
        changed_files=_changed_files(),
        coverage_report=_coverage_report(),
        test_results=TestResults(),
        failure_analysis=None,
        documentation_status=DocumentationStatus(updated=False, updated_files=[], skipped_reason="not ready"),
        deployment_decision=DeploymentDecision(
            status=DeploymentDecisionStatus.BLOCKED, reason="x", blocking_issues=["x"]
        ),
        generated_at=datetime.now(UTC),
    )
    assert report.deployment_decision.status == DeploymentDecisionStatus.BLOCKED
    assert Severity.HIGH.value == "high"
