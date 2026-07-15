"""Deterministic test-coverage detection for the Coverage Analysis Tool.

This never generates tests - it only reports whether tests already
exist for the changed files. task_manager has no test suite yet, so
the directory convention below is *prescribed* here rather than
inferred from existing structure:

- unit:        backend/tests/unit/
- integration: backend/tests/integration/
- e2e:         tests/e2e/          (pytest-playwright)
- performance: tests/performance/  (Locust)
"""

import re
from pathlib import Path

from app.models.enums import CoverageStatus
from app.models.state import ChangedFiles, CoverageReport

_STOPWORDS = {
    "app",
    "api",
    "routes",
    "service",
    "services",
    "repository",
    "repositories",
    "schema",
    "schemas",
    "model",
    "models",
    "components",
    "pages",
    "utils",
    "init",
    "test",
    "tests",
}


def _keywords(files: list[str]) -> set[str]:
    """Extract lowercase, stopword-filtered name tokens from changed file paths."""
    keywords: set[str] = set()
    for path in files:
        stem = Path(path).stem.lower()
        tokens = re.split(r"[_\-.\d]+", stem)
        keywords.update(token for token in tokens if token and token not in _STOPWORDS)
    return keywords


def _find_test_files(test_dir: Path) -> list[Path]:
    if not test_dir.is_dir():
        return []
    return sorted(test_dir.rglob("test_*.py")) + sorted(test_dir.rglob("*_test.py"))


def _find_locustfiles(perf_dir: Path) -> list[Path]:
    if not perf_dir.is_dir():
        return []
    return sorted(perf_dir.rglob("locustfile*.py"))


def _matches_keywords(test_file: Path, keywords: set[str]) -> bool:
    if not keywords:
        return False
    name_tokens = set(re.split(r"[_\-.\d]+", test_file.stem.lower()))
    return bool(name_tokens & keywords)


def _status_for_dir(test_dir: Path, keywords: set[str]) -> tuple[CoverageStatus, list[Path]]:
    test_files = _find_test_files(test_dir)
    if not test_files:
        return CoverageStatus.MISSING, []
    matching = [f for f in test_files if _matches_keywords(f, keywords)]
    if matching:
        return CoverageStatus.PRESENT, matching
    return CoverageStatus.MISSING, []


def analyze_coverage(repo_path: Path, changed_files: ChangedFiles) -> CoverageReport:
    """Check unit/integration/e2e/performance coverage for the changed files."""
    changed_paths = [fc.path for fc in changed_files.files]
    keywords = _keywords(changed_paths)
    frontend_changed = any(path.startswith("frontend/") for path in changed_paths)

    found: list[Path] = []

    unit_status, unit_files = _status_for_dir(repo_path / "backend" / "tests" / "unit", keywords)
    found.extend(unit_files)

    integration_status, integration_files = _status_for_dir(
        repo_path / "backend" / "tests" / "integration", keywords
    )
    found.extend(integration_files)

    if frontend_changed:
        e2e_status, e2e_files = _status_for_dir(repo_path / "tests" / "e2e", keywords)
        found.extend(e2e_files)
    else:
        e2e_status = CoverageStatus.NOT_REQUIRED

    perf_dir = repo_path / "tests" / "performance"
    locustfiles = _find_locustfiles(perf_dir)
    if not locustfiles:
        performance_status = CoverageStatus.NOT_REQUIRED
    else:
        matching_locustfiles = [f for f in locustfiles if _matches_keywords(f, keywords)]
        found.extend(matching_locustfiles)
        performance_status = CoverageStatus.PRESENT if matching_locustfiles else CoverageStatus.MISSING

    return CoverageReport(
        unit=unit_status,
        integration=integration_status,
        e2e=e2e_status,
        performance=performance_status,
        found_test_files=[str(f.relative_to(repo_path)) for f in found],
    )
