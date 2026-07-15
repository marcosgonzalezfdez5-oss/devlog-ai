"""Entry point for running one QA validation with the Deep Agent.

This is the seam a future FastAPI layer (Phase 5's `POST /analyze` and
`POST /run`) calls into - it doesn't exist yet, but this function is
already everything those routes will need.
"""

from langchain_core.messages import HumanMessage

from app.agent.configuration import generate_run_id
from app.agent.deep_agent import build_qa_agent
from app.config import LLMProvider


def run_qa_validation(
    feature_request: str,
    base_ref: str = "main",
    run_id: str | None = None,
    provider: LLMProvider | None = None,
) -> tuple[str, str]:
    """Run one QA validation end-to-end. Returns (final_message_text, run_id)."""
    run_id = run_id or generate_run_id()
    agent = build_qa_agent(provider)

    message = f"run_id: {run_id}\nbase_ref: {base_ref}\n\nFeature to validate:\n{feature_request}"
    result = agent.invoke({"messages": [HumanMessage(content=message)]})

    final_message = result["messages"][-1]
    return final_message.content, run_id
