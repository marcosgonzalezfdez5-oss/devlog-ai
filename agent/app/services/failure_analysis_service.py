"""Deterministic extraction of failure facts for the Failure Analysis Tool.

This only gathers *what* failed and its raw message - it never
explains *why* or assigns severity. Per CLAUDE.md's LLM-usage rules,
that narrative judgement belongs to the agent, which reads this
tool's output and authors a `TestFailure` per failure when it calls
`generate_report`.
"""

from app.models.enums import TestCategory
from app.models.state import FailureContext, TestResults

_COMPONENT_KEYWORDS: list[tuple[str, str]] = [
    ("task", "Task Management"),
    ("auth", "Authentication"),
    ("login", "Authentication"),
    ("dashboard", "Dashboard"),
    ("profile", "User Profiles"),
    ("user", "User Profiles"),
]


def _infer_component(test_name: str, category: TestCategory) -> str:
    lowered = test_name.lower()
    for keyword, component in _COMPONENT_KEYWORDS:
        if keyword in lowered:
            return component
    return f"{category.value} suite"


def extract_failure_context(test_results: TestResults) -> list[FailureContext]:
    """Collect one `FailureContext` per failed test case across all suites."""
    contexts: list[FailureContext] = []
    for suite in (test_results.unit, test_results.integration, test_results.e2e):
        if suite is None or not suite.executed:
            continue
        for case in suite.cases:
            if case.outcome != "failed":
                continue
            contexts.append(
                FailureContext(
                    test_name=case.name,
                    category=suite.category,
                    failure_message=case.failure_message or "(no failure message captured)",
                    affected_component=_infer_component(case.name, suite.category),
                )
            )
    return contexts
