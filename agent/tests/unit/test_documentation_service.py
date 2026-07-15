from pathlib import Path

from app.models.enums import DeploymentDecisionStatus
from app.models.reports import DeploymentDecision
from app.models.state import FeatureSummary
from app.services.documentation_service import update_documentation


def _feature_summary() -> FeatureSummary:
    return FeatureSummary(title="Task editing", description="Adds inline task editing.", affected_areas=["Task Management"])


def _write_decision(run_dir: Path, status: DeploymentDecisionStatus) -> None:
    decision = DeploymentDecision(status=status, reason="reason", blocking_issues=[])
    (run_dir / "deployment_decision.json").write_text(decision.model_dump_json(), encoding="utf-8")


def test_skips_when_no_decision_file_exists(tmp_path: Path):
    run_dir = tmp_path / "run"
    sut = tmp_path / "sut"
    run_dir.mkdir()
    sut.mkdir()

    status = update_documentation(run_dir, sut, _feature_summary(), "notes")

    assert status.updated is False
    assert not (sut / "README.md").exists()


def test_skips_when_decision_is_blocked(tmp_path: Path):
    run_dir = tmp_path / "run"
    sut = tmp_path / "sut"
    run_dir.mkdir()
    sut.mkdir()
    _write_decision(run_dir, DeploymentDecisionStatus.BLOCKED)

    status = update_documentation(run_dir, sut, _feature_summary(), "notes")

    assert status.updated is False
    assert not (sut / "README.md").exists()


def test_writes_readme_and_changelog_when_ready(tmp_path: Path):
    run_dir = tmp_path / "run"
    sut = tmp_path / "sut"
    run_dir.mkdir()
    sut.mkdir()
    _write_decision(run_dir, DeploymentDecisionStatus.READY)

    status = update_documentation(run_dir, sut, _feature_summary(), "Added task editing.")

    assert status.updated is True
    assert set(status.updated_files) == {"README.md", "CHANGELOG.md"}
    assert "Task editing" in (sut / "README.md").read_text(encoding="utf-8")
    assert "Added task editing." in (sut / "CHANGELOG.md").read_text(encoding="utf-8")


def test_second_ready_run_prepends_to_existing_docs(tmp_path: Path):
    run_dir = tmp_path / "run"
    sut = tmp_path / "sut"
    run_dir.mkdir()
    sut.mkdir()
    _write_decision(run_dir, DeploymentDecisionStatus.READY)

    update_documentation(run_dir, sut, _feature_summary(), "First change.")
    second_summary = FeatureSummary(title="Task deletion", description="Adds task deletion.", affected_areas=["Task Management"])
    update_documentation(run_dir, sut, second_summary, "Second change.")

    changelog = (sut / "CHANGELOG.md").read_text(encoding="utf-8")
    assert changelog.index("Task deletion") < changelog.index("Task editing")
