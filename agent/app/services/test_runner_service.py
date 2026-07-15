"""Deterministic test execution for the Test Runner Tool.

Unit, integration, and e2e all run through the same pytest mechanism -
Playwright E2E tests are `pytest-playwright`-based Python tests, not
the JS Playwright test runner, so one implementation covers all three,
just pointed at a different directory. Locust is a separate mechanism
since it reports throughput/latency rather than pass/fail test cases.
"""

import csv
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from app.models.enums import TestCategory
from app.models.state import PerformanceResult, TestCaseResult, TestSuiteResult


def _has_test_files(test_dir: Path) -> bool:
    return test_dir.is_dir() and any(test_dir.rglob("test_*.py"))


def _empty_suite(category: TestCategory, duration_seconds: float = 0.0) -> TestSuiteResult:
    return TestSuiteResult(
        category=category,
        executed=False,
        passed=0,
        failed=0,
        skipped=0,
        duration_seconds=duration_seconds,
        cases=[],
    )


def _parse_junit(category: TestCategory, junit_path: Path, fallback_duration: float) -> TestSuiteResult:
    if not junit_path.exists():
        return _empty_suite(category, fallback_duration)

    root = ET.parse(junit_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        return _empty_suite(category, fallback_duration)

    cases: list[TestCaseResult] = []
    passed = failed = skipped = 0
    for case in suite.findall("testcase"):
        name = case.get("name", "unknown")
        duration = float(case.get("time") or 0)
        failure = case.find("failure")
        error = case.find("error")
        skip = case.find("skipped")

        if failure is not None or error is not None:
            outcome = "failed"
            failed += 1
            node = failure if failure is not None else error
            message = node.get("message") or (node.text or "").strip()[:2000]
        elif skip is not None:
            outcome = "skipped"
            skipped += 1
            message = None
        else:
            outcome = "passed"
            passed += 1
            message = None

        cases.append(
            TestCaseResult(name=name, outcome=outcome, duration_seconds=duration, failure_message=message)
        )

    return TestSuiteResult(
        category=category,
        executed=True,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration_seconds=float(suite.get("time") or fallback_duration),
        cases=cases,
        raw_report_path=str(junit_path),
    )


def run_pytest_suite(category: TestCategory, test_dir: Path, run_dir: Path) -> TestSuiteResult:
    """Run pytest against `test_dir`, parsing results from a JUnit XML report.

    Returns `executed=False` without invoking pytest if `test_dir` has
    no `test_*.py` files, avoiding pytest's "no tests collected" exit
    code being mistaken for a failure.
    """
    if not _has_test_files(test_dir):
        return _empty_suite(category)

    junit_path = run_dir / f"{category.value}.xml"
    start = time.monotonic()
    subprocess.run(
        [sys.executable, "-m", "pytest", str(test_dir), f"--junitxml={junit_path}", "-q"],
        capture_output=True,
        text=True,
        check=False,
    )
    duration = time.monotonic() - start

    return _parse_junit(category, junit_path, fallback_duration=duration)


def _find_locustfile(performance_dir: Path) -> Path | None:
    if not performance_dir.is_dir():
        return None
    return next(iter(sorted(performance_dir.rglob("locustfile*.py"))), None)


def _as_float(value: str | None, default: float = 0.0) -> float:
    """Locust writes 'N/A' for percentile columns when there are zero successful requests."""
    try:
        return float(value) if value else default
    except ValueError:
        return default


def _parse_locust_stats(stats_path: Path) -> PerformanceResult:
    with stats_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    aggregated = next((row for row in rows if row.get("Name") == "Aggregated"), None)
    if aggregated is None:
        return PerformanceResult(executed=False, raw_report_path=str(stats_path))

    request_count = int(aggregated.get("Request Count") or 0)
    failure_count = int(aggregated.get("Failure Count") or 0)

    return PerformanceResult(
        executed=True,
        requests_per_second=_as_float(aggregated.get("Requests/s")),
        failure_rate=(failure_count / request_count) if request_count else 0.0,
        p95_latency_ms=_as_float(aggregated.get("95%")),
        raw_report_path=str(stats_path),
    )


def run_locust_suite(
    performance_dir: Path,
    run_dir: Path,
    host: str = "http://localhost:8000",
    users: int = 10,
    spawn_rate: int = 2,
    run_time: str = "30s",
) -> PerformanceResult:
    """Run a Locust load test if a locustfile exists under `performance_dir`."""
    locustfile = _find_locustfile(performance_dir)
    if locustfile is None:
        return PerformanceResult(executed=False)

    csv_prefix = run_dir / "performance"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "locust",
            "-f",
            str(locustfile),
            "--headless",
            "-u",
            str(users),
            "-r",
            str(spawn_rate),
            "--run-time",
            run_time,
            "--host",
            host,
            f"--csv={csv_prefix}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    stats_path = Path(f"{csv_prefix}_stats.csv")
    if not stats_path.exists():
        return PerformanceResult(executed=False)

    return _parse_locust_stats(stats_path)
