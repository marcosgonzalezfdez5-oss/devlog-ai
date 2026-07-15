"""FastAPI route tests. POST /run mocks the orchestrator (no LLM involved);
everything else runs the real deterministic code against isolated fixtures.
"""

import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes_module
from app.config import Settings
from app.main import app
from app.models.enums import DeploymentDecisionStatus
from app.models.reports import DeploymentDecision


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_against_sut_repo(client: TestClient, configured_settings: Settings):
    response = client.post("/analyze", json={"base_ref": "main"})

    assert response.status_code == 200
    body = response.json()
    assert "Task Management" in body["changed_files"]["affected_modules"]
    assert body["coverage_report"]["unit"] == "missing"


def test_reports_list_empty(client: TestClient, configured_settings: Settings):
    response = client.get("/reports")
    assert response.status_code == 200
    assert response.json() == {"reports": []}


def test_reports_detail_not_found(client: TestClient, configured_settings: Settings):
    response = client.get("/reports/no-such-run")
    assert response.status_code == 404


def test_run_returns_expected_response_with_orchestrator_mocked(
    client: TestClient, configured_settings: Settings, monkeypatch: pytest.MonkeyPatch
):
    run_id = "api-test-run"
    run_dir = configured_settings.reports_dir / run_id
    run_dir.mkdir(parents=True)
    decision = DeploymentDecision(status=DeploymentDecisionStatus.READY, reason="all good", blocking_issues=[])
    (run_dir / "deployment_decision.json").write_text(decision.model_dump_json(), encoding="utf-8")

    def fake_run_qa_validation(feature_request, base_ref="main", run_id=None, provider=None):
        return "Validation complete.", "api-test-run"

    monkeypatch.setattr(routes_module, "run_qa_validation", fake_run_qa_validation)

    response = client.post("/run", json={"feature_request": "Validate task editing"})

    assert response.status_code == 200
    body = response.json()
    assert body == {"run_id": "api-test-run", "message": "Validation complete.", "deployment_status": "ready"}


def test_run_wraps_agent_failure_as_502(
    client: TestClient, configured_settings: Settings, monkeypatch: pytest.MonkeyPatch
):
    def failing_run_qa_validation(feature_request, base_ref="main", run_id=None, provider=None):
        raise RuntimeError("boom")

    monkeypatch.setattr(routes_module, "run_qa_validation", failing_run_qa_validation)

    response = client.post("/run", json={"feature_request": "Validate task editing"})

    assert response.status_code == 502
