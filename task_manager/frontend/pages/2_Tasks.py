"""Tasks page: filterable task table with create/edit/delete/status actions."""

import streamlit as st

from components.sidebar import render_sidebar
from components.task_form import create_task_dialog
from components.task_table import render_task_table
from services import task_service, user_service
from services.api_client import ApiError
from utils.session import require_auth

st.set_page_config(page_title="Tasks - Task Manager", layout="wide")
require_auth()
render_sidebar()

st.title("Tasks")

try:
    users = user_service.list_users()
except ApiError as exc:
    st.error(f"Could not load users: {exc.message}")
    st.stop()

users_by_id = {user["id"]: user["full_name"] for user in users}
status_options = ["All", "Pending", "In Progress", "Review", "Completed"]
assignee_options = ["All"] + [user["id"] for user in users]

filter_cols = st.columns([2, 2, 1])
status_filter = filter_cols[0].selectbox("Filter by status", status_options)
assignee_filter = filter_cols[1].selectbox(
    "Filter by assignee",
    assignee_options,
    format_func=lambda uid: "All" if uid == "All" else users_by_id.get(uid, uid),
)
filter_cols[2].write("")
if filter_cols[2].button("New Task", use_container_width=True):
    create_task_dialog(users)

try:
    tasks = task_service.list_tasks(
        status=None if status_filter == "All" else status_filter,
        assigned_to=None if assignee_filter == "All" else assignee_filter,
    )
except ApiError as exc:
    st.error(f"Could not load tasks: {exc.message}")
else:
    render_task_table(tasks, users_by_id, users)
