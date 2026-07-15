"""Shared enums used across the QA agent's workflow-state models.

Kept separate from the models themselves (added in Phase 2) because
this vocabulary is referenced by multiple future modules (tools,
state, reports) and shouldn't be duplicated or redefined per-module.
"""

from enum import StrEnum


class TestCategory(StrEnum):
    """Categories of test coverage the Coverage Analysis Tool checks for."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"


class Severity(StrEnum):
    """Severity of a test failure, assigned by the Failure Analysis Tool."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeploymentDecisionStatus(StrEnum):
    """Final deployment recommendation produced at the end of a QA run."""

    READY = "ready"
    BLOCKED = "blocked"


class CoverageStatus(StrEnum):
    """Per-category test coverage status reported by the Coverage Analysis Tool."""

    PRESENT = "present"
    MISSING = "missing"
    NOT_REQUIRED = "not_required"
