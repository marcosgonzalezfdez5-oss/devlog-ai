"""Centralized logging configuration for the AI QA Deep Agent."""

import logging

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger. Call once on application startup.

    Never logs API keys, tokens, or other secrets - only module-level
    messages emitted explicitly by application code (agent reasoning
    steps, tool execution, timings, errors).
    """
    logging.basicConfig(level=logging.getLevelName(level), format=LOG_FORMAT)
