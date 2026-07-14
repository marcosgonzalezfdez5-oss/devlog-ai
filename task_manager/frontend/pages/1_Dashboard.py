"""Dashboard page: task statistics and recent tasks."""

import streamlit as st

from components.sidebar import render_sidebar
from components.stat_cards import render_stat_cards
from services import dashboard_service, user_service
from services.api_client import ApiError
from utils.session import require_auth

st.set_page_config(page_title="Dashboard - Task Manager", layout="wide")
require_auth()
render_sidebar()

st.title("Dashboard")

try:
    data = dashboard_service.get_dashboard()
    users = user_service.list_users()
except ApiError as exc:
    st.error(f"Could not load dashboard: {exc.message}")
else:
    render_stat_cards(data["stats"])

    st.subheader("Recent Tasks")
    users_by_id = {u["id"]: u["full_name"] for u in users}
    recent_tasks = data["recent_tasks"]

    if not recent_tasks:
        st.info("No tasks yet.")
    else:
        st.dataframe(
            [
                {
                    "Title": task["title"],
                    "Priority": task["priority"],
                    "Status": task["status"],
                    "Assigned User": users_by_id.get(task["assigned_to"], "Unknown"),
                    "Created": task["created_at"][:10],
                }
                for task in recent_tasks
            ],
            use_container_width=True,
            hide_index=True,
        )
