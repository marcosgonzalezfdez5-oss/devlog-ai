"""LangChain tool adapter for the Documentation Tool."""

from langchain_core.tools import tool

from app.config import get_settings
from app.models.state import ChangedFiles, FeatureSummary
from app.services import documentation_service
from app.utils.run_artifacts import get_run_dir, read_artifact, write_artifact


@tool
def update_documentation(
    run_id: str, feature_title: str, feature_description: str, release_notes: str
) -> str:
    """Update task_manager's README.md and CHANGELOG.md - only if READY.

    Independently re-checks this run's `deployment_decision.json` and
    refuses to write anything if the decision is BLOCKED, regardless
    of what you believe the outcome was. Call `decide_deployment` first.

    Args:
        run_id: This run's identifier.
        feature_title: Short human-readable feature name.
        feature_description: One or two sentences on what changed.
        release_notes: Changelog-style summary of the change for users.
    """
    changed_files = read_artifact(run_id, "changed_files.json", ChangedFiles)
    feature_summary = FeatureSummary(
        title=feature_title,
        description=feature_description,
        affected_areas=changed_files.affected_modules,
    )

    status = documentation_service.update_documentation(
        get_run_dir(run_id), get_settings().sut_repo_path, feature_summary, release_notes
    )
    write_artifact(run_id, "documentation_status.json", status)

    if not status.updated:
        return f"Documentation NOT updated: {status.skipped_reason}"
    return f"Documentation updated: {', '.join(status.updated_files)}"
