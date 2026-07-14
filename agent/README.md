# AI QA Deep Agent

An autonomous QA engineer that validates changes to [`task_manager/`](../task_manager)
before deployment: it analyzes git diffs, checks test coverage, runs existing tests,
explains failures, updates documentation on success, and produces a QA report with a
READY/BLOCKED deployment decision.

Architecture: **one Deep Agent (LLM reasoning) orchestrating deterministic Python
tools (execution)**. The agent never runs commands, parses output, or calculates
metrics itself, and it never modifies application source code, generates tests, or
fixes bugs. See [`.claude/CLAUDE.md`](.claude/CLAUDE.md) for the full architecture.

This is v0, built incrementally. Current status: **Phase 1 — project skeleton**
(config, logging, LLM provider factory, shared enums). Tools, the agent itself,
the API, and the agent's own tests follow in later phases.

## Setup

```bash
cd agent
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env    # then fill in the API key for your chosen LLM_PROVIDER
```

## LLM provider

`app/utils/llm_factory.py` builds a LangChain chat model from `LLM_PROVIDER`
(`anthropic` | `openai` | `gemini`) so the agent isn't locked to one vendor —
swap providers (e.g. Claude for reasoning, Gemini Flash for cheap steps) via
config, no code changes.
