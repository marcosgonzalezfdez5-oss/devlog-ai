"""Performance tests for the Task Manager backend, driven with Locust.

Targets GET /tasks and POST /tasks directly on the FastAPI backend (not through
the Streamlit frontend, since Locust load-tests HTTP APIs and Streamlit's
websocket-based session model isn't a fit for it).

All simulated users share a single login token obtained once up front, rather than
each calling POST /login independently: Supabase Auth rate-limits sign-ins per
account, and 50 concurrent logins against the same test user reliably triggered 401s
unrelated to /tasks performance (confirmed empirically). The test is about /tasks
throughput, not login throughput, so auth is deliberately kept out of the load.

Assumes the backend is already running (see task_manager/start.ps1 / start.sh).
"""

from gevent import monkey

monkey.patch_all()

import os
from uuid import uuid4

import requests
from dotenv import load_dotenv
from gevent.pool import Pool
from locust import HttpUser, between, task
from locust.env import Environment

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
TEST_USER_EMAIL = os.environ["TEST_USER_EMAIL"]
TEST_USER_PASSWORD = os.environ["TEST_USER_PASSWORD"]

USERS = 50
SPAWN_RATE = 10
RUN_TIME_SECONDS = 120
P95_THRESHOLD_MS = 1000
TITLE_PREFIX = "perf-test-"
CLEANUP_CONCURRENCY = 20


def _login() -> tuple[str, dict[str, str]]:
    response = requests.post(
        f"{BACKEND_URL}/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        timeout=10,
    )
    response.raise_for_status()
    body = response.json()
    return body["user_id"], {"Authorization": f"Bearer {body['access_token']}"}


class PerfUser(HttpUser):
    host = BACKEND_URL
    wait_time = between(0.5, 1.5)
    user_id: str = ""
    headers: dict[str, str] = {}

    @task(3)
    def list_tasks(self) -> None:
        self.client.get("/tasks", headers=self.headers, name="/tasks [GET]")

    @task(1)
    def create_task(self) -> None:
        self.client.post(
            "/tasks",
            headers=self.headers,
            name="/tasks [POST]",
            json={
                "title": f"{TITLE_PREFIX}{uuid4()}",
                "description": "Created by the performance test suite.",
                "priority": "Low",
                "assigned_to": self.user_id,
            },
        )


def _cleanup_created_tasks(headers: dict[str, str]) -> None:
    # Sweep by title prefix rather than tracking IDs from Locust responses: under load
    # some connections get reset before the response body is read (a real capacity
    # limit of the single-process dev server), which would otherwise leave orphaned
    # rows that a response-tracking approach could never know to delete.
    tasks = requests.get(f"{BACKEND_URL}/tasks", headers=headers, timeout=10).json()
    task_ids = [t["id"] for t in tasks if t["title"].startswith(TITLE_PREFIX)]
    if not task_ids:
        return

    def delete_one(task_id: str) -> None:
        requests.delete(f"{BACKEND_URL}/tasks/{task_id}", headers=headers, timeout=10)

    Pool(CLEANUP_CONCURRENCY).map(delete_one, task_ids)


def test_performance_thresholds() -> None:
    """Runs a 50-user, 2-minute load test against /tasks and asserts p95 < 1s with no failures."""
    user_id, headers = _login()
    PerfUser.user_id = user_id
    PerfUser.headers = headers

    env = Environment(user_classes=[PerfUser])
    runner = env.create_local_runner()

    runner.start(USERS, spawn_rate=SPAWN_RATE)
    runner.greenlet.join(timeout=RUN_TIME_SECONDS)
    runner.quit()

    try:
        stats = env.stats.total
        p95 = stats.get_response_time_percentile(0.95)
        assert p95 < P95_THRESHOLD_MS, f"p95 response time {p95}ms exceeded {P95_THRESHOLD_MS}ms"
        assert stats.num_failures == 0, f"{stats.num_failures} requests failed during the load test"
    finally:
        _cleanup_created_tasks(headers)
