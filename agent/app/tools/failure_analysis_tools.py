"""LangChain tool adapter for the Failure Analysis Tool."""

from langchain_core.tools import tool

from app.models.state import FailureContextBundle, TestResults
from app.services import failure_analysis_service
from app.utils.run_artifacts import read_artifact, write_artifact


@tool
def extract_failure_context(run_id: str) -> str:
    """Gather the raw facts about every failed test in this run.

    Only call this if a prior test-runner tool reported failures. This
    tool never explains *why* a test failed - read its output and
    author that explanation yourself when calling `generate_report`.
    """
    test_results = read_artifact(run_id, "test_results.json", TestResults)
    contexts = failure_analysis_service.extract_failure_context(test_results)
    write_artifact(run_id, "failure_context.json", FailureContextBundle(items=contexts))

    if not contexts:
        return "No failed tests found."

    lines = [
        f"- [{c.category.value}] {c.test_name} ({c.affected_component}): {c.failure_message}"
        for c in contexts
    ]
    return "\n".join(lines)
