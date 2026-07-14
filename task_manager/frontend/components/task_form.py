"""Create/edit task dialogs."""

import streamlit as st

from services import task_service
from services.api_client import ApiError

_PRIORITY_OPTIONS = ["Low", "Medium", "High"]
_STATUS_OPTIONS = ["Pending", "In Progress", "Review", "Completed"]


def _user_label(users: list[dict], user_id: str) -> str:
    return next((u["full_name"] for u in users if u["id"] == user_id), user_id)


@st.dialog("Create Task")
def create_task_dialog(users: list[dict]) -> None:
    with st.form("create_task_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", _PRIORITY_OPTIONS)
        assigned_to = st.selectbox(
            "Assigned To",
            options=[u["id"] for u in users],
            format_func=lambda uid: _user_label(users, uid),
        )
        submitted = st.form_submit_button("Create")

    if not submitted:
        return
    if not title.strip():
        st.error("Title is required.")
        return

    try:
        task_service.create_task(
            {
                "title": title,
                "description": description or None,
                "priority": priority,
                "assigned_to": assigned_to,
            }
        )
    except ApiError as exc:
        st.error(exc.message)
        return
    st.rerun()


@st.dialog("Edit Task")
def edit_task_dialog(task: dict, users: list[dict]) -> None:
    user_ids = [u["id"] for u in users]

    with st.form("edit_task_form"):
        title = st.text_input("Title", value=task["title"])
        description = st.text_area("Description", value=task.get("description") or "")
        priority = st.selectbox(
            "Priority", _PRIORITY_OPTIONS, index=_PRIORITY_OPTIONS.index(task["priority"])
        )
        status = st.selectbox(
            "Status", _STATUS_OPTIONS, index=_STATUS_OPTIONS.index(task["status"])
        )
        assigned_to = st.selectbox(
            "Assigned To",
            options=user_ids,
            index=user_ids.index(task["assigned_to"]) if task["assigned_to"] in user_ids else 0,
            format_func=lambda uid: _user_label(users, uid),
        )
        submitted = st.form_submit_button("Save")

    if not submitted:
        return
    if not title.strip():
        st.error("Title is required.")
        return

    try:
        task_service.update_task(
            task["id"],
            {
                "title": title,
                "description": description or None,
                "priority": priority,
                "status": status,
                "assigned_to": assigned_to,
            },
        )
    except ApiError as exc:
        st.error(exc.message)
        return
    st.rerun()
