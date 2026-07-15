"""LangChain tool adapter for the Deployment Decision Tool."""

from langchain_core.tools import tool

from app.models.state import CoverageReport, TestResults
from app.services.deployment_decision_service import decide
from app.utils.run_artifacts import read_artifact, write_artifact


@tool
def decide_deployment(run_id: str) -> str:
    """Compute the READY/BLOCKED deployment decision for this run.

    Pure rule-based on `coverage_report.json` and `test_results.json` -
    takes no arguments describing the outcome, so it can't be talked
    into the wrong answer. Call after all test-runner tools have run.
    """
    coverage_report = read_artifact(run_id, "coverage_report.json", CoverageReport)
    test_results = read_artifact(run_id, "test_results.json", TestResults)

    decision = decide(coverage_report, test_results)
    write_artifact(run_id, "deployment_decision.json", decision)

    return f"{decision.status.value.upper()}: {decision.reason}"
