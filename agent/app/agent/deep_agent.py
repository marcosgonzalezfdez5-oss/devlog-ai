"""Assembles the single QA Deep Agent that orchestrates every tool in app/tools/."""

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

from app.agent.configuration import TOOLS
from app.agent.prompts import SYSTEM_PROMPT
from app.config import LLMProvider
from app.utils.llm_factory import get_chat_model
from deepagents import create_deep_agent


def build_qa_agent(
    provider: LLMProvider | None = None, model: BaseChatModel | None = None
) -> CompiledStateGraph:
    """Build the compiled QA Deep Agent graph.

    `model` overrides `provider`/`get_chat_model` entirely when given -
    this is the seam tests use to pass in a scripted fake chat model
    without touching any other wiring.

    No custom backend is configured, so the built-in `execute` shell
    tool stays inert (the default `StateBackend` doesn't implement
    sandboxed execution) - the agent can only act through the tools in
    `TOOLS`, which is what structurally enforces "the agent must never
    run commands itself."
    """
    return create_deep_agent(
        model=model or get_chat_model(provider),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="qa-deep-agent",
    )
