"""Deterministic Markdown rendering and persistence for the Reporting Tool.

Purely a formatting step: by the time this runs, every field on the
`QAReport` was already produced by an earlier deterministic tool or
authored by the agent as this tool's own arguments - no new LLM call
happens here.
"""

from pathlib import Path

from app.models.enums import CoverageStatus
from app.models.reports import QAReport
from app.models.state import PerformanceResult, TestSuiteResult


def _suite_line(label: str, suite: TestSuiteResult | None) -> str:
    if suite is None or not suite.executed:
        return f"{label}:\nNot executed\n"
    return f"{label}:\n{suite.passed} Passed, {suite.failed} Failed, {suite.skipped} Skipped\n"


def _performance_line(performance: PerformanceResult | None, coverage_status: CoverageStatus) -> str:
    if coverage_status == CoverageStatus.NOT_REQUIRED:
        return "Performance:\nNot required\n"
    if performance is None or not performance.executed:
        return "Performance:\nNot executed\n"
    if (performance.failure_rate or 0) > 0:
        return f"Performance:\n{performance.failure_rate:.1%} failure rate, p95={performance.p95_latency_ms:.0f}ms\n"
    return f"Performance:\nPassed ({performance.requests_per_second:.1f} req/s, p95={performance.p95_latency_ms:.0f}ms)\n"


def render_markdown(report: QAReport) -> str:
    """Render a `QAReport` as Markdown, matching CLAUDE.md's example format."""
    lines = [
        "# QA Report",
        "",
        "## Feature",
        "",
        report.feature_summary.title,
        "",
        report.feature_summary.description,
        "",
        f"Affected areas: {', '.join(report.feature_summary.affected_areas) or 'None identified'}",
        "",
        "## Changed Files",
        "",
        f"{len(report.changed_files.files)} file(s) changed "
        f"({report.changed_files.base_ref} -> {report.changed_files.target_ref})",
        "",
        "## Coverage",
        "",
        f"Unit: {report.coverage_report.unit.value}",
        f"Integration: {report.coverage_report.integration.value}",
        f"E2E: {report.coverage_report.e2e.value}",
        f"Performance: {report.coverage_report.performance.value}",
        "",
        "## Tests",
        "",
        _suite_line("Unit Tests", report.test_results.unit),
        _suite_line("Integration Tests", report.test_results.integration),
        _suite_line("E2E Tests", report.test_results.e2e),
        _performance_line(report.test_results.performance, report.coverage_report.performance),
    ]

    if report.failure_analysis and report.failure_analysis.failures:
        lines += ["## Failure Analysis", "", report.failure_analysis.summary, ""]
        for failure in report.failure_analysis.failures:
            lines += [
                f"### {failure.test_name} ({failure.severity.value})",
                "",
                f"Expected: {failure.expected or 'N/A'}",
                f"Actual: {failure.actual or 'N/A'}",
                f"Possible cause: {failure.possible_cause}",
                f"Affected component: {failure.affected_component}",
                "",
            ]

    lines += [
        "## Documentation",
        "",
        "Updated" if report.documentation_status.updated else f"Not updated ({report.documentation_status.skipped_reason})",
        "",
        "## Deployment",
        "",
        report.deployment_decision.status.value.upper(),
        "",
        report.deployment_decision.reason,
        "",
        f"_Generated {report.generated_at.isoformat()}_",
    ]

    return "\n".join(lines)


def write_report(run_dir: Path, report: QAReport) -> Path:
    """Write `qa_report.md` and `qa_report.json` to the run directory."""
    (run_dir / "qa_report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")

    markdown = render_markdown(report)
    markdown_path = run_dir / "qa_report.md"
    markdown_path.write_text(markdown, encoding="utf-8")
    return markdown_path
