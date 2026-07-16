"""Application configuration loaded from environment variables."""

from functools import lru_cache
import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


LLMProvider = Literal["anthropic", "openai", "gemini"]

_AGENT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """Environment-backed settings for the AI QA Deep Agent."""

    llm_provider: LLMProvider = os.getenv("LLM_PROVIDER")

    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5")

    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")

    sut_repo_path: Path = _AGENT_ROOT.parent / "task_manager"
    reports_dir: Path = _AGENT_ROOT / "docs" / "reports"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (single source of truth for config)."""
    return Settings()
