"""Chains the real @tool objects end-to-end, mirroring Phase 3's manual verification."""

from app.config import Settings
from app.tools.coverage_tools import analyze_test_coverage
from app.tools.deployment_tools import decide_deployment
from app.tools.documentation_tools import update_documentation
from app.tools.git_tools import analyze_git_changes
from app.tools.test_tools import run_e2e_tests, run_integration_tests, run_performance_tests, run_unit_tests

RUN_ID = "integration-test-run"


def _run_chain_up_to_decision(run_id: str) -> str:
    analyze_git_changes.invoke({"run_id": run_id, "base_ref": "main"})
    analyze_test_coverage.invoke({"run_id": run_id})
    run_unit_tests.invoke({"run_id": run_id})
    run_integration_tests.invoke({"run_id": run_id})
    run_e2e_tests.invoke({"run_id": run_id})
    run_performance_tests.invoke({"run_id": run_id})
    return decide_deployment.invoke({"run_id": run_id})


def test_pipeline_blocks_when_integration_coverage_is_missing(configured_settings: Settings):
    unit_dir = configured_settings.sut_repo_path / "backend" / "tests" / "unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "test_tasks.py").write_text("def test_tasks(): assert True\n", encoding="utf-8")

    result = _run_chain_up_to_decision(RUN_ID)

    assert result.startswith("BLOCKED")
    assert "Integration" in result

    doc_result = update_documentation.invoke(
        {
            "run_id": RUN_ID,
            "feature_title": "Task editing",
            "feature_description": "Adds validation.",
            "release_notes": "Added validation.",
        }
    )
    assert "NOT updated" in doc_result
    assert not (configured_settings.sut_repo_path / "README.md").exists()


def test_pipeline_reaches_ready_once_integration_coverage_exists(configured_settings: Settings):
    unit_dir = configured_settings.sut_repo_path / "backend" / "tests" / "unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "test_tasks.py").write_text("def test_tasks(): assert True\n", encoding="utf-8")

    integration_dir = configured_settings.sut_repo_path / "backend" / "tests" / "integration"
    integration_dir.mkdir(parents=True)
    (integration_dir / "test_tasks.py").write_text("def test_tasks_integration(): assert True\n", encoding="utf-8")

    run_id = f"{RUN_ID}-ready"
    result = _run_chain_up_to_decision(run_id)

    assert result.startswith("READY")

    doc_result = update_documentation.invoke(
        {
            "run_id": run_id,
            "feature_title": "Task editing",
            "feature_description": "Adds validation.",
            "release_notes": "Added validation.",
        }
    )
    assert "Documentation updated" in doc_result
    assert (configured_settings.sut_repo_path / "README.md").exists()
