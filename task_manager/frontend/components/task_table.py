"""Interactive tasks table: inline status change, edit, and delete actions."""

import streamlit as st

from components.task_form import edit_task_dialog
from services import task_service
from services.api_client import ApiError

_STATUS_OPTIONS = ["Pending", "In Progress", "Review", "Completed"]
_COLUMN_WIDTHS = [3, 4, 1, 2, 2, 2, 1, 1]
_HEADERS = ["Title", "Description", "Priority", "Status", "Assigned User", "Created", "", ""]


def render_task_table(tasks: list[dict], users_by_id: dict[str, str], users: list[dict]) -> None:
    if not tasks:
        st.info("No tasks match the current filters.")
        return

    header_cols = st.columns(_COLUMN_WIDTHS)
    for col, label in zip(header_cols, _HEADERS):
        if label:
            col.markdown(f"**{label}**")

    for task in tasks:
        cols = st.columns(_COLUMN_WIDTHS)
        cols[0].write(task["title"])
        cols[1].write(task.get("description") or "-")
        cols[2].write(task["priority"])

        new_status = cols[3].selectbox(
            "Status",
            _STATUS_OPTIONS,
            index=_STATUS_OPTIONS.index(task["status"]),
            key=f"status_{task['id']}",
            label_visibility="collapsed",
        )
        if new_status != task["status"]:
            try:
                task_service.update_status(task["id"], new_status)
            except ApiError as exc:
                st.error(exc.message)
            else:
                st.rerun()

        cols[4].write(users_by_id.get(task["assigned_to"], "Unknown"))
        cols[5].write(task["created_at"][:10])

        if cols[6].button("Edit", key=f"edit_{task['id']}"):
            edit_task_dialog(task, users)

        if cols[7].button("Delete", key=f"delete_{task['id']}"):
            try:
                task_service.delete_task(task["id"])
            except ApiError as exc:
                st.error(exc.message)
            else:
                st.rerun()
