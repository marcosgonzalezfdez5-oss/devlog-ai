"""Shared pytest fixtures for the QA agent's own test suite."""

import subprocess
from pathlib import Path

import pytest

from app.config import get_settings


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def sut_repo(tmp_path: Path) -> Path:
    """Build a temp git repo with a `main` branch and a feature branch with real diffs.

    Returns the path to the `task_manager/` subdirectory within it, so
    it's a drop-in stand-in for `settings.sut_repo_path`.
    """
    repo_root = tmp_path / "repo"
    sut = repo_root / "task_manager"
    (sut / "backend" / "app" / "api" / "routes").mkdir(parents=True)

    _git("init", "-q", "-b", "main", cwd=repo_root)
    _git("config", "user.email", "test@test.com", cwd=repo_root)
    _git("config", "user.name", "test", cwd=repo_root)

    tasks_py = sut / "backend" / "app" / "api" / "routes" / "tasks.py"
    tasks_py.write_text("print('v1')\n", encoding="utf-8")
    _git("add", "-A", cwd=repo_root)
    _git("commit", "-q", "-m", "init", cwd=repo_root)

    _git("checkout", "-q", "-b", "feature/edit-task", cwd=repo_root)
    tasks_py.write_text("print('v1')\nprint('v2 - added validation')\n", encoding="utf-8")
    (sut / "backend" / "app" / "api" / "routes" / "new_file.py").write_text("print('new')\n", encoding="utf-8")
    _git("add", "-A", cwd=repo_root)
    _git("commit", "-q", "-m", "feat: add validation", cwd=repo_root)

    return sut


@pytest.fixture
def isolated_reports_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point `settings.reports_dir` at a temp directory for the duration of a test."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(reports_dir))
    get_settings.cache_clear()
    yield reports_dir
    get_settings.cache_clear()


@pytest.fixture
def configured_settings(sut_repo: Path, isolated_reports_dir: Path, monkeypatch: pytest.MonkeyPatch):
    """Point `settings.sut_repo_path` and `settings.reports_dir` at temp fixtures.

    Use this (instead of `sut_repo`/`isolated_reports_dir` directly)
    whenever the code under test calls `get_settings()` itself, e.g.
    the `@tool`-wrapped functions in `app/tools/`.
    """
    monkeypatch.setenv("SUT_REPO_PATH", str(sut_repo))
    get_settings.cache_clear()
    yield get_settings()
    get_settings.cache_clear()
