from pathlib import Path

from app.services.git_service import analyze_changes


def test_analyze_changes_detects_committed_and_new_files(sut_repo: Path):
    result = analyze_changes(sut_repo, base_ref="main")

    paths = {f.path: f.change_type for f in result.files}
    assert paths["backend/app/api/routes/tasks.py"] == "modified"
    assert paths["backend/app/api/routes/new_file.py"] == "added"


def test_analyze_changes_maps_known_paths_to_task_management(sut_repo: Path):
    result = analyze_changes(sut_repo, base_ref="main")
    assert "Task Management" in result.affected_modules


def test_analyze_changes_falls_back_gracefully_on_unknown_base_ref(sut_repo: Path):
    result = analyze_changes(sut_repo, base_ref="does-not-exist")
    # Falls back to working-tree-only diff instead of raising.
    assert isinstance(result.files, list)
