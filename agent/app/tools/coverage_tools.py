"""LangChain tool adapter for the Coverage Analysis Tool."""

from langchain_core.tools import tool

from app.config import get_settings
from app.models.state import ChangedFiles
from app.services.coverage_service import analyze_coverage
from app.utils.run_artifacts import read_artifact, write_artifact


@tool
def analyze_test_coverage(run_id: str) -> str:
    """Check whether existing tests cover this run's changed files.

    Never generates tests - only reports PRESENT/MISSING/NOT_REQUIRED
    per category (unit, integration, e2e, performance). Requires
    `analyze_git_changes` to have run first in this `run_id`.
    """
    changed_files = read_artifact(run_id, "changed_files.json", ChangedFiles)
    coverage_report = analyze_coverage(get_settings().sut_repo_path, changed_files)
    write_artifact(run_id, "coverage_report.json", coverage_report)

    return (
        f"unit={coverage_report.unit.value}, "
        f"integration={coverage_report.integration.value}, "
        f"e2e={coverage_report.e2e.value}, "
        f"performance={coverage_report.performance.value}"
    )
