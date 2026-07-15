"""Shared helpers for reading/writing a QA run's on-disk artifacts.

Every tool that produces structured data writes it as JSON under
`reports_dir/<run_id>/`, and downstream tools read it back from there
instead of requiring the LLM to retype it as tool-call arguments. This
module centralizes that read/write so each service doesn't repeat the
same path-joining and (de)serialization logic.
"""

from pathlib import Path

from pydantic import BaseModel

from app.config import get_settings


def get_run_dir(run_id: str) -> Path:
    """Return the artifact directory for a run, creating it if needed."""
    run_dir = get_settings().reports_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_artifact(run_id: str, filename: str, model: BaseModel) -> Path:
    """Serialize a model to `<run_dir>/<filename>` and return the path."""
    path = get_run_dir(run_id) / filename
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
    return path


def read_artifact[T: BaseModel](run_id: str, filename: str, model_cls: type[T]) -> T:
    """Read and validate `<run_dir>/<filename>` as `model_cls`.

    Raises `FileNotFoundError` if the artifact doesn't exist yet, which
    surfaces as a clear tool error when a tool is called out of order
    (e.g. `decide_deployment` before `run_unit_tests`).
    """
    path = get_run_dir(run_id) / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing artifact '{filename}' for run '{run_id}'. "
            "Call the tool that produces it first."
        )
    return model_cls.model_validate_json(path.read_text(encoding="utf-8"))
