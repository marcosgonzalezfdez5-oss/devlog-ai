from app.models.enums import CoverageStatus, DeploymentDecisionStatus, TestCategory
from app.models.state import CoverageReport, PerformanceResult, TestResults, TestSuiteResult
from app.services.deployment_decision_service import decide


def _coverage(**overrides) -> CoverageReport:
    base = {
        "unit": CoverageStatus.NOT_REQUIRED,
        "integration": CoverageStatus.NOT_REQUIRED,
        "e2e": CoverageStatus.NOT_REQUIRED,
        "performance": CoverageStatus.NOT_REQUIRED,
        "found_test_files": [],
    }
    base.update(overrides)
    return CoverageReport(**base)


def _passing_suite() -> TestSuiteResult:
    return TestSuiteResult(
        category=TestCategory.UNIT, executed=True, passed=3, failed=0, skipped=0, duration_seconds=1.0, cases=[]
    )


def test_blocked_when_coverage_missing():
    decision = decide(_coverage(unit=CoverageStatus.MISSING), TestResults())
    assert decision.status == DeploymentDecisionStatus.BLOCKED
    assert "Unit" in decision.blocking_issues[0]


def test_blocked_when_coverage_present_but_not_executed():
    decision = decide(_coverage(unit=CoverageStatus.PRESENT), TestResults())
    assert decision.status == DeploymentDecisionStatus.BLOCKED


def test_blocked_when_suite_has_failures():
    suite = _passing_suite()
    suite.failed = 2
    decision = decide(_coverage(unit=CoverageStatus.PRESENT), TestResults(unit=suite))
    assert decision.status == DeploymentDecisionStatus.BLOCKED


def test_ready_when_everything_required_passes():
    decision = decide(
        _coverage(unit=CoverageStatus.PRESENT, integration=CoverageStatus.PRESENT),
        TestResults(unit=_passing_suite(), integration=_passing_suite()),
    )
    assert decision.status == DeploymentDecisionStatus.READY
    assert decision.blocking_issues == []


def test_blocked_when_performance_coverage_missing():
    decision = decide(_coverage(performance=CoverageStatus.MISSING), TestResults())
    assert decision.status == DeploymentDecisionStatus.BLOCKED


def test_blocked_when_performance_failure_rate_too_high():
    perf = PerformanceResult(executed=True, requests_per_second=10, failure_rate=0.5, p95_latency_ms=100)
    decision = decide(_coverage(performance=CoverageStatus.PRESENT), TestResults(performance=perf))
    assert decision.status == DeploymentDecisionStatus.BLOCKED


def test_ready_when_performance_failure_rate_acceptable():
    perf = PerformanceResult(executed=True, requests_per_second=10, failure_rate=0.0, p95_latency_ms=100)
    decision = decide(_coverage(performance=CoverageStatus.PRESENT), TestResults(performance=perf))
    assert decision.status == DeploymentDecisionStatus.READY
