"""Deterministic documentation updates for the Documentation Tool.

Writes only run only after a successful validation - enforced here in
code, not left to the agent's good behavior: this function reads the
run's own `DeploymentDecision` and refuses to write anything if it
isn't READY, regardless of what the caller claims.
"""

import datetime
from pathlib import Path

from app.models.enums import DeploymentDecisionStatus
from app.models.reports import DeploymentDecision
from app.models.state import DocumentationStatus, FeatureSummary

_README_MARKER = "## Recent Changes"
_CHANGELOG_HEADER = "# Changelog\n"


def _update_readme(sut_repo_path: Path, entry: str) -> None:
    readme_path = sut_repo_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
    else:
        content = "# Task Manager\n"

    if _README_MARKER in content:
        lines = content.splitlines()
        idx = lines.index(_README_MARKER)
        lines.insert(idx + 1, entry)
        content = "\n".join(lines) + "\n"
    else:
        content = content.rstrip("\n") + f"\n\n{_README_MARKER}\n{entry}\n"

    readme_path.write_text(content, encoding="utf-8")


def _update_changelog(sut_repo_path: Path, heading: str, release_notes: str) -> None:
    changelog_path = sut_repo_path / "CHANGELOG.md"
    existing = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else _CHANGELOG_HEADER
    if existing.startswith(_CHANGELOG_HEADER):
        existing = existing[len(_CHANGELOG_HEADER) :].lstrip("\n")

    new_entry = f"{heading}\n\n{release_notes}\n"
    changelog_path.write_text(f"{_CHANGELOG_HEADER}\n{new_entry}\n{existing}".rstrip() + "\n", encoding="utf-8")


def update_documentation(
    run_dir: Path,
    sut_repo_path: Path,
    feature_summary: FeatureSummary,
    release_notes: str,
) -> DocumentationStatus:
    """Update `README.md` and `CHANGELOG.md`, only if this run's decision is READY."""
    decision_path = run_dir / "deployment_decision.json"
    if not decision_path.exists():
        return DocumentationStatus(
            updated=False,
            updated_files=[],
            skipped_reason="No deployment decision found for this run; call decide_deployment first.",
        )

    decision = DeploymentDecision.model_validate_json(decision_path.read_text(encoding="utf-8"))
    if decision.status != DeploymentDecisionStatus.READY:
        return DocumentationStatus(
            updated=False,
            updated_files=[],
            skipped_reason=f"Deployment decision was {decision.status.value.upper()}; documentation not updated.",
        )

    today = datetime.date.today().isoformat()
    _update_readme(sut_repo_path, f"- **{today}** - {feature_summary.title}: {feature_summary.description}")
    _update_changelog(sut_repo_path, f"## {today} - {feature_summary.title}", release_notes)

    return DocumentationStatus(updated=True, updated_files=["README.md", "CHANGELOG.md"], skipped_reason=None)
