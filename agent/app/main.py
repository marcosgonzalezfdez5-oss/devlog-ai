"""FastAPI entrypoint for the AI QA Deep Agent."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import get_settings
from app.logging_config import configure_logging
from app.utils.exceptions import AgentExecutionError, AppError, NotFoundError

configure_logging(get_settings().log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI QA Deep Agent")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log method, path, status code, and duration for every request."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(AgentExecutionError)
async def agent_execution_error_handler(request: Request, exc: AgentExecutionError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": exc.message})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Catch-all for any AppError subclass without a more specific handler."""
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Never leak internal exception details to the client."""
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(router)
