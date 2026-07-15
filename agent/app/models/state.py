"""Strongly-typed workflow-state models produced by the QA agent's tools.

Each model corresponds to the output of exactly one deterministic tool
(see `app/tools/`). Fields are explicit rather than dict-shaped, per
CLAUDE.md's "avoid unstructured dictionaries" rule.
"""

from typing import Literal

from pydantic import BaseModel

from app.models.enums import CoverageStatus, Severity, TestCategory


class FileChange(BaseModel):
    """A single file changed between two git refs (or in the working tree)."""

    path: str
    change_type: Literal["added", "modified", "deleted"]


class ChangedFiles(BaseModel):
    """Output of the Git Analysis Tool."""

    base_ref: str
    target_ref: str
    files: list[FileChange]
    affected_modules: list[str]


class FeatureSummary(BaseModel):
    """LLM-authored summary of what the changed files implement."""

    title: str
    description: str
    affected_areas: list[str]


class CoverageReport(BaseModel):
    """Output of the Coverage Analysis Tool."""

    unit: CoverageStatus
    integration: CoverageStatus
    e2e: CoverageStatus
    performance: CoverageStatus
    found_test_files: list[str]


class TestCaseResult(BaseModel):
    """A single test case's outcome, parsed from a JUnit report."""

    name: str
    outcome: Literal["passed", "failed", "skipped"]
    duration_seconds: float
    failure_message: str | None = None


class TestSuiteResult(BaseModel):
    """Aggregated result of running one test category via pytest."""

    category: TestCategory
    executed: bool
    passed: int
    failed: int
    skipped: int
    duration_seconds: float
    cases: list[TestCaseResult]
    raw_report_path: str | None = None


class PerformanceResult(BaseModel):
    """Aggregated result of a Locust performance run."""

    executed: bool
    requests_per_second: float | None = None
    failure_rate: float | None = None
    p95_latency_ms: float | None = None
    raw_report_path: str | None = None


class TestResults(BaseModel):
    """Output of the Test Runner Tool across all categories."""

    unit: TestSuiteResult | None = None
    integration: TestSuiteResult | None = None
    e2e: TestSuiteResult | None = None
    performance: PerformanceResult | None = None

    @property
    def all_required_passed(self) -> bool:
        """True if every executed pytest-based suite has zero failures.

        Performance is excluded: it reports throughput/latency, not a
        pass/fail outcome, so it never blocks this check on its own.
        """
        suites = [self.unit, self.integration, self.e2e]
        return all(suite is None or not suite.executed or suite.failed == 0 for suite in suites)


class FailureContext(BaseModel):
    """Deterministic facts about one failed test, before LLM narrative is added."""

    test_name: str
    category: TestCategory
    failure_message: str
    affected_component: str


class TestFailure(BaseModel):
    """LLM-authored explanation of one failed test, supplied to the Reporting Tool."""

    test_name: str
    category: TestCategory
    expected: str | None
    actual: str | None
    possible_cause: str
    affected_component: str
    severity: Severity


class FailureAnalysis(BaseModel):
    """LLM-authored explanation of all failures in a run."""

    failures: list[TestFailure]
    summary: str


class FailureContextBundle(BaseModel):
    """Wrapper so `list[FailureContext]` can be persisted as one JSON artifact."""

    items: list[FailureContext]


class DocumentationStatus(BaseModel):
    """Output of the Documentation Tool."""

    updated: bool
    updated_files: list[str]
    skipped_reason: str | None = None
