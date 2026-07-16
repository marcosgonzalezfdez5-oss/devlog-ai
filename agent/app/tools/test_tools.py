"""LangChain tool adapters for the Test Runner Tool.

Each tool runs one category and merges its result into this run's
shared `test_results.json`, since the four categories are called as
separate tool invocations but contribute to one `TestResults` model.
"""

from langchain_core.tools import tool

from app.config import get_settings
from app.models.enums import TestCategory
from app.models.state import TestResults
from app.services.test_runner_service import run_locust_suite, run_pytest_suite
from app.utils.run_artifacts import get_run_dir, read_artifact, write_artifact


def _load_test_results(run_id: str) -> TestResults:
    try:
        return read_artifact(run_id, "test_results.json", TestResults)
    except FileNotFoundError:
        return TestResults()


def _summarize(label: str, executed: bool, passed: int = 0, failed: int = 0, skipped: int = 0) -> str:
    if not executed:
        return f"{label}: no tests found - not executed."
    return f"{label}: {passed} passed, {failed} failed, {skipped} skipped."


@tool
def run_unit_tests(run_id: str) -> str:
    """Run unit tests (tasks/unit) via pytest and record the result."""
    sut_repo_path = get_settings().sut_repo_path
    run_dir = get_run_dir(run_id)
    result = run_pytest_suite(TestCategory.UNIT, sut_repo_path / "tasks" / "unit", run_dir)

    results = _load_test_results(run_id)
    results.unit = result
    write_artifact(run_id, "test_results.json", results)

    return _summarize("Unit tests", result.executed, result.passed, result.failed, result.skipped)


@tool
def run_integration_tests(run_id: str) -> str:
    """Run integration tests (tasks/integration) via pytest and record the result."""
    sut_repo_path = get_settings().sut_repo_path
    run_dir = get_run_dir(run_id)
    result = run_pytest_suite(
        TestCategory.INTEGRATION, sut_repo_path / "tasks" / "integration", run_dir
    )

    results = _load_test_results(run_id)
    results.integration = result
    write_artifact(run_id, "test_results.json", results)

    return _summarize("Integration tests", result.executed, result.passed, result.failed, result.skipped)


@tool
def run_e2e_tests(run_id: str) -> str:
    """Run end-to-end tests (tasks/e2e) via pytest-playwright and record the result."""
    sut_repo_path = get_settings().sut_repo_path
    run_dir = get_run_dir(run_id)
    result = run_pytest_suite(TestCategory.E2E, sut_repo_path / "tasks" / "e2e", run_dir)

    results = _load_test_results(run_id)
    results.e2e = result
    write_artifact(run_id, "test_results.json", results)

    return _summarize("E2E tests", result.executed, result.passed, result.failed, result.skipped)


@tool
def run_performance_tests(run_id: str) -> str:
    """Run performance tests (tasks/performance) via Locust and record the result."""
    sut_repo_path = get_settings().sut_repo_path
    run_dir = get_run_dir(run_id)
    result = run_locust_suite(sut_repo_path / "tasks" / "performance", run_dir)

    results = _load_test_results(run_id)
    results.performance = result
    write_artifact(run_id, "test_results.json", results)

    if not result.executed:
        return "Performance tests: no locustfile found - not executed."
    return (
        f"Performance tests: {result.requests_per_second:.1f} req/s, "
        f"{result.failure_rate:.1%} failure rate, p95={result.p95_latency_ms:.0f}ms."
    )
