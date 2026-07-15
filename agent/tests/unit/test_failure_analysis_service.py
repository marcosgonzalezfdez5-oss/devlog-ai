from app.models.enums import TestCategory
from app.models.state import TestCaseResult, TestResults, TestSuiteResult
from app.services.failure_analysis_service import extract_failure_context


def _suite(name: str, outcome: str, category: TestCategory = TestCategory.UNIT) -> TestSuiteResult:
    return TestSuiteResult(
        category=category,
        executed=True,
        passed=0 if outcome == "failed" else 1,
        failed=1 if outcome == "failed" else 0,
        skipped=0,
        duration_seconds=0.1,
        cases=[TestCaseResult(name=name, outcome=outcome, duration_seconds=0.1, failure_message="boom" if outcome == "failed" else None)],
    )


def test_extracts_only_failed_cases():
    results = TestResults(unit=_suite("test_create_task", "failed"))
    contexts = extract_failure_context(results)

    assert len(contexts) == 1
    assert contexts[0].test_name == "test_create_task"
    assert contexts[0].affected_component == "Task Management"


def test_ignores_passed_and_skipped_cases():
    results = TestResults(unit=_suite("test_ok", "passed"))
    assert extract_failure_context(results) == []


def test_ignores_unexecuted_suites():
    suite = _suite("test_x", "failed")
    suite.executed = False
    results = TestResults(unit=suite)
    assert extract_failure_context(results) == []


def test_falls_back_to_category_label_when_no_keyword_matches():
    results = TestResults(unit=_suite("test_xyz_totally_unrelated", "failed"))
    contexts = extract_failure_context(results)
    assert contexts[0].affected_component == "unit suite"
