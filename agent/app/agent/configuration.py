"""Fixed configuration for the QA Deep Agent: its run-id scheme and tool list."""

import uuid

from app.tools.coverage_tools import analyze_test_coverage
from app.tools.deployment_tools import decide_deployment
from app.tools.documentation_tools import update_documentation
from app.tools.failure_analysis_tools import extract_failure_context
from app.tools.git_tools import analyze_git_changes
from app.tools.reporting_tools import generate_report
from app.tools.test_tools import (
    run_e2e_tests,
    run_integration_tests,
    run_performance_tests,
    run_unit_tests,
)

TOOLS = [
    analyze_git_changes,
    analyze_test_coverage,
    run_unit_tests,
    run_integration_tests,
    run_e2e_tests,
    run_performance_tests,
    decide_deployment,
    extract_failure_context,
    update_documentation,
    generate_report,
]


def generate_run_id() -> str:
    """Generate a short, unique identifier shared by every tool call in a run."""
    return uuid.uuid4().hex[:12]
