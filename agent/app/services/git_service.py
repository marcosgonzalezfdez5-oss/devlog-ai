"""Deterministic git-diff analysis for the Git Analysis Tool.

`task_manager/` is not its own git repository - it's a subdirectory of
the enclosing `devlog-ai` repo - so this locates the repo from
`sut_repo_path` upward and filters diff entries back down to it.
"""

import logging
from pathlib import Path, PurePosixPath

import git

from app.models.state import ChangedFiles, FileChange

logger = logging.getLogger(__name__)

_STATUS_MAP: dict[str, str] = {
    "A": "added",
    "M": "modified",
    "D": "deleted",
}

# First substring match wins; order matters. Mirrors task_manager's fixed
# feature set (task_manager/.claude/CLAUDE.md) since it has no other
# documented module boundary to infer from.
_MODULE_MAP: list[tuple[str, str]] = [
    ("backend/app/api/routes/auth", "Authentication"),
    ("backend/app/services/auth_service", "Authentication"),
    ("backend/app/models/auth", "Authentication"),
    ("backend/app/schemas/auth", "Authentication"),
    ("backend/app/api/routes/tasks", "Task Management"),
    ("backend/app/services/task_service", "Task Management"),
    ("backend/app/repositories/task_repository", "Task Management"),
    ("backend/app/models/task", "Task Management"),
    ("backend/app/schemas/task", "Task Management"),
    ("backend/app/api/routes/dashboard", "Dashboard"),
    ("backend/app/services/dashboard_service", "Dashboard"),
    ("backend/app/schemas/dashboard", "Dashboard"),
    ("backend/app/api/routes/users", "User Profiles"),
    ("backend/app/services/profile_service", "User Profiles"),
    ("backend/app/repositories/profile_repository", "User Profiles"),
    ("backend/app/models/profile", "User Profiles"),
    ("backend/app/schemas/user", "User Profiles"),
    ("frontend/pages/2_tasks", "Task Frontend UI"),
    ("frontend/components/task_", "Task Frontend UI"),
    ("frontend/services/task_service", "Task Frontend UI"),
    ("frontend/pages/1_dashboard", "Dashboard Frontend UI"),
    ("frontend/components/stat_cards", "Dashboard Frontend UI"),
    ("frontend/services/dashboard_service", "Dashboard Frontend UI"),
    ("frontend/components/sidebar", "Frontend Shell"),
    ("frontend/utils/session", "Frontend Shell"),
    ("frontend/services/auth_service", "Frontend Shell"),
    ("supabase-schema", "Database Schema"),
]


def _map_module(path: str) -> str:
    """Map a changed file's path to a human-readable feature area."""
    lowered = path.lower()
    for prefix, module in _MODULE_MAP:
        if prefix in lowered:
            return module
    return "General"


def _parse_name_status(output: str) -> dict[str, str]:
    """Parse `git diff --name-status` output into `{path: change_type}`.

    Renames (`R100\told\tnew`) are treated as a modification of the new
    path - the QA agent cares about which files changed, not history.
    """
    changes: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        code, paths = parts[0], parts[1:]
        if code.startswith("R") or code.startswith("C"):
            changes[paths[-1]] = "modified"
        else:
            changes[paths[0]] = _STATUS_MAP.get(code[0], "modified")
    return changes


def analyze_changes(sut_repo_path: Path, base_ref: str = "main") -> ChangedFiles:
    """Diff `base_ref...HEAD` unioned with the current working-tree diff.

    Falls back to a working-tree-only diff if `base_ref` can't be
    resolved (e.g. no such branch), so the tool never hard-fails on an
    unusual repo state.
    """
    repo = git.Repo(sut_repo_path, search_parent_directories=True)
    repo_root = Path(repo.working_dir)
    sut_relative = sut_repo_path.resolve().relative_to(repo_root.resolve())

    changes: dict[str, str] = {}
    target_ref = repo.head.commit.hexsha[:12]

    try:
        committed_output = repo.git.diff(f"{base_ref}...HEAD", "--name-status")
        changes.update(_parse_name_status(committed_output))
    except git.GitCommandError:
        logger.warning("Could not diff against base_ref=%r; using working tree only.", base_ref)

    working_tree_output = repo.git.diff("HEAD", "--name-status")
    changes.update(_parse_name_status(working_tree_output))

    sut_prefix = PurePosixPath(sut_relative.as_posix())
    file_changes: list[FileChange] = []
    for path, change_type in changes.items():
        posix_path = PurePosixPath(path)
        if sut_prefix not in posix_path.parents and posix_path != sut_prefix:
            continue
        relative_to_sut = posix_path.relative_to(sut_prefix)
        file_changes.append(FileChange(path=str(relative_to_sut), change_type=change_type))  # type: ignore[arg-type]

    affected_modules = sorted({_map_module(fc.path) for fc in file_changes})

    return ChangedFiles(
        base_ref=base_ref,
        target_ref=target_ref,
        files=file_changes,
        affected_modules=affected_modules,
    )
