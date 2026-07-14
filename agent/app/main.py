"""FastAPI entrypoint for the AI QA Deep Agent.

Routes are added in Phase 5 (GET /health, POST /analyze, POST /run,
GET /reports, GET /reports/{id}). This module only proves the app
boots cleanly on top of Phase 1's config and logging setup.
"""

from fastapi import FastAPI

from app.logging_config import configure_logging
from app.config import get_settings

configure_logging(get_settings().log_level)

app = FastAPI(title="AI QA Deep Agent")
