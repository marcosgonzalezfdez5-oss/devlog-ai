"""LangChain tool adapter for the Git Analysis Tool."""

from langchain_core.tools import tool

from app.config import get_settings
from app.services.git_service import analyze_changes
from app.utils.run_artifacts import write_artifact


@tool
def analyze_git_changes(run_id: str, base_ref: str = "main") -> str:
    """Analyze what changed in the System Under Test for this QA run.

    Diffs `base_ref...HEAD` unioned with any uncommitted working-tree
    changes, filtered to the System Under Test's directory. Call this
    first in every run - later tools rely on `changed_files.json`.

    Args:
        run_id: Identifier for this QA run; shared across all tool calls.
        base_ref: Branch/commit to diff against (default "main").
    """
    changed_files = analyze_changes(get_settings().sut_repo_path, base_ref=base_ref)
    write_artifact(run_id, "changed_files.json", changed_files)

    if not changed_files.files:
        return "No changes detected against the System Under Test."
    return (
        f"{len(changed_files.files)} file(s) changed across "
        f"{', '.join(changed_files.affected_modules) or 'no identified modules'}."
    )
