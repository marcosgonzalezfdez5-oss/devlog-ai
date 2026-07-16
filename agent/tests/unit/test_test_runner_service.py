import sys
from pathlib import Path

from app.models.enums import TestCategory
from app.services.test_runner_service import _parse_locust_stats, _resolve_python_executable, run_pytest_suite


def test_resolve_python_executable_falls_back_to_agent_interpreter_without_a_venv(tmp_path: Path):
    assert _resolve_python_executable(tmp_path) == sys.executable


def test_resolve_python_executable_prefers_sibling_venv(tmp_path: Path):
    scripts_dir = tmp_path / "venv" / "Scripts"
    scripts_dir.mkdir(parents=True)
    fake_python = scripts_dir / "python.exe"
    fake_python.write_text("", encoding="utf-8")

    assert _resolve_python_executable(tmp_path) == str(fake_python)


def test_returns_not_executed_when_no_test_files(tmp_path: Path):
    empty_dir = tmp_path / "unit"
    empty_dir.mkdir()

    result = run_pytest_suite(TestCategory.UNIT, empty_dir, tmp_path)

    assert result.executed is False
    assert result.passed == 0
    assert result.failed == 0


def test_collects_monolithic_category_file_not_matching_test_glob(tmp_path: Path):
    """task_manager's real convention: `unit.py`, not `test_unit.py`."""
    test_dir = tmp_path / "unit"
    test_dir.mkdir()
    (test_dir / "unit.py").write_text(
        "def test_pass(): assert 1 + 1 == 2\n",
        encoding="utf-8",
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    result = run_pytest_suite(TestCategory.UNIT, test_dir, run_dir)

    assert result.executed is True
    assert result.passed == 1
    assert result.failed == 0


def test_parses_passed_failed_and_skipped_cases(tmp_path: Path):
    test_dir = tmp_path / "unit"
    test_dir.mkdir()
    (test_dir / "test_sample.py").write_text(
        "import pytest\n"
        "def test_pass(): assert 1 + 1 == 2\n"
        "def test_fail(): assert 1 + 1 == 3\n"
        "def test_skip(): pytest.skip('skip on purpose')\n",
        encoding="utf-8",
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    result = run_pytest_suite(TestCategory.UNIT, test_dir, run_dir)

    assert result.executed is True
    assert result.passed == 1
    assert result.failed == 1
    assert result.skipped == 1
    outcomes = {c.name: c.outcome for c in result.cases}
    assert outcomes["test_pass"] == "passed"
    assert outcomes["test_fail"] == "failed"
    assert outcomes["test_skip"] == "skipped"
    failed_case = next(c for c in result.cases if c.name == "test_fail")
    assert failed_case.failure_message is not None


def test_parse_locust_stats_handles_normal_row(tmp_path: Path):
    csv_path = tmp_path / "stats.csv"
    csv_path.write_text(
        "Type,Name,Request Count,Failure Count,Requests/s,95%\n"
        ",Aggregated,100,5,10.5,250\n",
        encoding="utf-8",
    )

    result = _parse_locust_stats(csv_path)

    assert result.executed is True
    assert result.requests_per_second == 10.5
    assert result.failure_rate == 0.05
    assert result.p95_latency_ms == 250.0


def test_parse_locust_stats_handles_na_percentiles(tmp_path: Path):
    csv_path = tmp_path / "stats.csv"
    csv_path.write_text(
        "Type,Name,Request Count,Failure Count,Requests/s,95%\n"
        ",Aggregated,0,0,0.0,N/A\n",
        encoding="utf-8",
    )

    result = _parse_locust_stats(csv_path)

    assert result.executed is True
    assert result.p95_latency_ms == 0.0
    assert result.failure_rate == 0.0
