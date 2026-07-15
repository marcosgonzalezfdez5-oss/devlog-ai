"""Final, run-terminal models: the deployment decision and the QA report."""

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DeploymentDecisionStatus
from app.models.state import (
    ChangedFiles,
    CoverageReport,
    DocumentationStatus,
    FailureAnalysis,
    FeatureSummary,
    TestResults,
)


class DeploymentDecision(BaseModel):
    """Output of the Deployment Decision Tool. Never LLM-authored."""

    status: DeploymentDecisionStatus
    reason: str
    blocking_issues: list[str]


class QAReport(BaseModel):
    """Output of the Reporting Tool - the final artifact of a QA run."""

    feature_summary: FeatureSummary
    changed_files: ChangedFiles
    coverage_report: CoverageReport
    test_results: TestResults
    failure_analysis: FailureAnalysis | None
    documentation_status: DocumentationStatus
    deployment_decision: DeploymentDecision
    generated_at: datetime
    markdown_path: str | None = None
