"""LangChain tool adapter for the Reporting Tool - the terminal tool of a run."""

from datetime import UTC, datetime

from langchain_core.tools import tool

from app.models.reports import DeploymentDecision, QAReport
from app.models.state import (
    ChangedFiles,
    CoverageReport,
    DocumentationStatus,
    FailureAnalysis,
    FeatureSummary,
    TestFailure,
    TestResults,
)
from app.services.reporting_service import write_report
from app.utils.run_artifacts import get_run_dir, read_artifact


@tool
def generate_report(
    run_id: str,
    feature_title: str,
    feature_description: str,
    failure_summary: str | None = None,
    failures: list[TestFailure] | None = None,
) -> str:
    """Assemble and persist the final QA report for this run. Always call last.

    Combines every artifact already produced by earlier tools in this
    run (changed files, coverage, test results, deployment decision,
    documentation status) with your authored narrative: the feature
    summary, and - if any tests failed - your explanation of each one.

    Args:
        run_id: This run's identifier.
        feature_title: Short human-readable feature name.
        feature_description: One or two sentences on what the change does.
        failure_summary: Overall summary of failures, if any occurred.
        failures: Your explanation of each failed test (expected/actual/cause/severity),
            informed by `extract_failure_context`'s output. Omit if nothing failed.
    """
    changed_files = read_artifact(run_id, "changed_files.json", ChangedFiles)
    coverage_report = read_artifact(run_id, "coverage_report.json", CoverageReport)
    test_results = read_artifact(run_id, "test_results.json", TestResults)
    deployment_decision = read_artifact(run_id, "deployment_decision.json", DeploymentDecision)

    try:
        documentation_status = read_artifact(run_id, "documentation_status.json", DocumentationStatus)
    except FileNotFoundError:
        documentation_status = DocumentationStatus(
            updated=False, updated_files=[], skipped_reason="Documentation tool was not called for this run."
        )

    feature_summary = FeatureSummary(
        title=feature_title,
        description=feature_description,
        affected_areas=changed_files.affected_modules,
    )

    failure_analysis = None
    if failures:
        failure_analysis = FailureAnalysis(
            failures=failures, summary=failure_summary or "See individual failure details below."
        )

    run_dir = get_run_dir(run_id)
    report = QAReport(
        feature_summary=feature_summary,
        changed_files=changed_files,
        coverage_report=coverage_report,
        test_results=test_results,
        failure_analysis=failure_analysis,
        documentation_status=documentation_status,
        deployment_decision=deployment_decision,
        generated_at=datetime.now(UTC),
        markdown_path=str(run_dir / "qa_report.md"),
    )

    markdown_path = write_report(run_dir, report)
    return markdown_path.read_text(encoding="utf-8")
