"""Pure, rule-based deployment gate for the Deployment Decision Tool.

Deliberately takes no LLM-authored input: this is exactly the kind of
"calculating metrics" decision CLAUDE.md says must never go through
the LLM. Given the same coverage report and test results, this always
returns the same decision.
"""

from app.models.enums import CoverageStatus, DeploymentDecisionStatus
from app.models.reports import DeploymentDecision
from app.models.state import CoverageReport, TestResults

_MAX_ACCEPTABLE_PERFORMANCE_FAILURE_RATE = 0.05


def decide(coverage_report: CoverageReport, test_results: TestResults) -> DeploymentDecision:
    """BLOCKED if any required category is missing coverage, unexecuted, or failing."""
    blocking_issues: list[str] = []

    for label, coverage_status, suite in (
        ("Unit", coverage_report.unit, test_results.unit),
        ("Integration", coverage_report.integration, test_results.integration),
        ("E2E", coverage_report.e2e, test_results.e2e),
    ):
        if coverage_status == CoverageStatus.MISSING:
            blocking_issues.append(f"{label} test coverage is missing.")
        elif coverage_status == CoverageStatus.NOT_REQUIRED:
            continue
        elif suite is None or not suite.executed:
            blocking_issues.append(f"{label} tests were not executed.")
        elif suite.failed > 0:
            blocking_issues.append(f"{label} tests have {suite.failed} failing test(s).")

    if coverage_report.performance == CoverageStatus.MISSING:
        blocking_issues.append("Performance test coverage is missing.")
    elif coverage_report.performance == CoverageStatus.PRESENT:
        perf = test_results.performance
        if perf is None or not perf.executed:
            blocking_issues.append("Performance tests were not executed.")
        elif (perf.failure_rate or 0) > _MAX_ACCEPTABLE_PERFORMANCE_FAILURE_RATE:
            blocking_issues.append(f"Performance tests have a {perf.failure_rate:.1%} failure rate.")

    if blocking_issues:
        return DeploymentDecision(
            status=DeploymentDecisionStatus.BLOCKED,
            reason=" ".join(blocking_issues),
            blocking_issues=blocking_issues,
        )

    return DeploymentDecision(
        status=DeploymentDecisionStatus.READY,
        reason="All required tests passed and coverage requirements are satisfied.",
        blocking_issues=[],
    )
