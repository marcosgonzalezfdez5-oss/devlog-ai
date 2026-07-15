"""End-to-end test for the Task Manager, driven through the real Streamlit UI with Playwright.

Covers the core lifecycle: log in, create a task, verify it appears in the list,
and change its status.

Cleanup deletes the created task via a direct backend API call rather than a second
UI click. A UI-driven delete right after the status-change interaction was found to be
unreliable in this app - Streamlit occasionally drops a widget click that arrives while
a previous interaction's rerun is still settling, so the DELETE request never reaches the
backend at all (confirmed by polling the API directly after the click). That's a real,
reproducible flakiness in the Tasks page worth flagging separately; it isn't something an
E2E test should paper over by retrying, so cleanup here does not depend on it.

Assumes the frontend and backend are already running (see task_manager/start.ps1 / start.sh).
"""

import os
from uuid import uuid4

import requests
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:8501")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
TEST_USER_EMAIL = os.environ["TEST_USER_EMAIL"]
TEST_USER_PASSWORD = os.environ["TEST_USER_PASSWORD"]


def _delete_task_by_title(title: str) -> None:
    response = requests.post(
        f"{BACKEND_URL}/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        timeout=10,
    )
    response.raise_for_status()
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    tasks = requests.get(f"{BACKEND_URL}/tasks", headers=headers, timeout=10).json()
    for task in tasks:
        if task["title"] == title:
            requests.delete(f"{BACKEND_URL}/tasks/{task['id']}", headers=headers, timeout=10)


def test_create_task_and_update_status(page: Page) -> None:
    task_title = f"e2e-test-{uuid4()}"

    try:
        page.goto(FRONTEND_URL)
        page.get_by_role("textbox", name="Email").fill(TEST_USER_EMAIL)
        page.get_by_role("textbox", name="Password").fill(TEST_USER_PASSWORD)
        page.get_by_role("button", name="Log in").click()

        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # Streamlit renders both its own auto-generated multipage nav and the app's
        # custom st.page_link sidebar, so scope to the latter to avoid ambiguity.
        page.get_by_test_id("stSidebarUserContent").get_by_role("link", name="Tasks").click()
        expect(page.get_by_role("heading", name="Tasks")).to_be_visible()

        dialog = page.get_by_role("dialog")
        page.get_by_role("button", name="New Task").click()
        dialog.get_by_role("textbox", name="Title").fill(task_title)
        dialog.get_by_role("button", name="Create").click()
        # Streamlit's rerun after a form submit is slower than a typical SPA update,
        # so wait for the dialog to close before looking for the new row.
        expect(dialog).to_be_hidden(timeout=20000)

        row = page.locator("div[data-testid='stHorizontalBlock']").filter(has_text=task_title)
        expect(row).to_be_visible(timeout=20000)

        row.get_by_role("combobox").click()
        page.get_by_role("option", name="In Progress").click()
        # Streamlit's status selectbox is a BaseWeb combobox <input>; its displayed value
        # lives in aria-label ("Selected <value>. Status"), not the element's text content.
        expect(row.get_by_role("combobox")).to_have_attribute(
            "aria-label", "Selected In Progress. Status", timeout=20000
        )
    finally:
        _delete_task_by_title(task_title)
