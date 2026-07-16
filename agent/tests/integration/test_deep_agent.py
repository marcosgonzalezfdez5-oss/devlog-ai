"""Drives the real compiled Deep Agent graph with a scripted fake chat model.

Only the LLM is mocked - `deepagents`/LangGraph wiring, and every tool
in `app/tools/`, run for real. The fake model never calls the built-in
optional tools (`write_todos`, `task`, filesystem tools), which is a
valid model choice, not a workaround - so the full middleware stack
assembled by `create_deep_agent` runs untouched.
"""

from collections.abc import Iterator

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.deep_agent import build_qa_agent
from app.config import Settings
from app.models.enums import DeploymentDecisionStatus
from app.models.reports import QAReport


class ScriptedToolCallingChatModel(GenericFakeChatModel):
    """`GenericFakeChatModel` doesn't implement `bind_tools`; this makes it a no-op
    passthrough so `create_agent` can bind tools to it without erroring."""

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self


def _tool_call(name: str, args: dict, call_id: str) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def _scripted_messages(run_id: str) -> Iterator[AIMessage]:
    steps = [
        ("analyze_git_changes", {"run_id": run_id, "base_ref": "main"}),
        ("analyze_test_coverage", {"run_id": run_id}),
        ("run_unit_tests", {"run_id": run_id}),
        ("run_integration_tests", {"run_id": run_id}),
        ("run_e2e_tests", {"run_id": run_id}),
        ("run_performance_tests", {"run_id": run_id}),
        ("decide_deployment", {"run_id": run_id}),
        (
            "update_documentation",
            {
                "run_id": run_id,
                "feature_title": "Task editing",
                "feature_description": "Adds validation.",
                "release_notes": "Added validation.",
            },
        ),
        (
            "generate_report",
            {
                "run_id": run_id,
                "feature_title": "Task editing",
                "feature_description": "Adds validation.",
            },
        ),
    ]
    for i, (name, args) in enumerate(steps):
        yield _tool_call(name, args, call_id=f"call_{i}")
    yield AIMessage(content="QA validation complete. Deployment decision recorded.")


def test_deep_agent_runs_full_tool_sequence_with_scripted_model(configured_settings: Settings):
    unit_dir = configured_settings.sut_repo_path / "tasks" / "unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "test_tasks.py").write_text("def test_tasks(): assert True\n", encoding="utf-8")
    integration_dir = configured_settings.sut_repo_path / "tasks" / "integration"
    integration_dir.mkdir(parents=True)
    (integration_dir / "test_tasks.py").write_text("def test_tasks_integration(): assert True\n", encoding="utf-8")

    run_id = "fake-model-run"
    fake_model = ScriptedToolCallingChatModel(messages=_scripted_messages(run_id))
    agent = build_qa_agent(model=fake_model)

    result = agent.invoke(
        {"messages": [HumanMessage(content=f"run_id: {run_id}\nbase_ref: main\n\nValidate task editing.")]}
    )

    assert result["messages"][-1].content == "QA validation complete. Deployment decision recorded."

    report_path = configured_settings.reports_dir / run_id / "qa_report.json"
    assert report_path.exists()
    report = QAReport.model_validate_json(report_path.read_text(encoding="utf-8"))
    assert report.deployment_decision.status == DeploymentDecisionStatus.READY
