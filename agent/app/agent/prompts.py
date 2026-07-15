"""Loads the QA agent's system prompt from `prompts/` (no inline prompts in Python)."""

from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"

SYSTEM_PROMPT = (_PROMPTS_DIR / "qa_agent_system_prompt.md").read_text(encoding="utf-8")
