"""Centralized logging configuration for the Task Manager API."""

import logging

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger. Call once on application startup.

    Never logs request bodies, headers, passwords, or tokens - only
    module-level messages emitted explicitly by application code.
    """
    logging.basicConfig(level=level, format=LOG_FORMAT)
