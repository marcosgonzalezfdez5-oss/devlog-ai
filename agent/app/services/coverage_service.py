"""Deterministic test-coverage detection for the Coverage Analysis Tool.

This never generates tests - it only reports whether tests already
exist for the changed files. task_manager's test suite lives at:

- unit:        tasks/unit/         (monolithic unit.py)
- integration: tasks/integration/  (monolithic integration.py)
- e2e:         tasks/e2e/          (monolithic e2e.py, pytest-playwright)
- performance: tasks/performance/  (monolithic performance.py, Locust)

Each category is a single file covering every feature rather than one
file per feature, so presence of that file is treated as coverage for
the whole category - the per-feature keyword match below only applies
as a fallback for directories that instead hold multiple `test_*.py`/
`*_test.py` files.
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


def _status_for_dir(test_dir: Path, keywords: set[str], category_name: str) -> tuple[CoverageStatus, list[Path]]:
    monolithic_file = test_dir / f"{category_name}.py"
    if monolithic_file.is_file():
        return CoverageStatus.PRESENT, [monolithic_file]

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

    unit_status, unit_files = _status_for_dir(repo_path / "tasks" / "unit", keywords, "unit")
    found.extend(unit_files)

    integration_status, integration_files = _status_for_dir(
        repo_path / "tasks" / "integration", keywords, "integration"
    )
    found.extend(integration_files)

    if frontend_changed:
        e2e_status, e2e_files = _status_for_dir(repo_path / "tasks" / "e2e", keywords, "e2e")
        found.extend(e2e_files)
    else:
        e2e_status = CoverageStatus.NOT_REQUIRED

    perf_dir = repo_path / "tasks" / "performance"
    monolithic_perf_file = perf_dir / "performance.py"
    if monolithic_perf_file.is_file():
        found.append(monolithic_perf_file)
        performance_status = CoverageStatus.PRESENT
    else:
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
