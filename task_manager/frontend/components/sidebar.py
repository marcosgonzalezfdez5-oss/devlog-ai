"""Sidebar navigation shared across authenticated pages."""

import streamlit as st

from utils.session import clear_session


def render_sidebar() -> None:
    with st.sidebar:
        st.page_link("pages/1_Dashboard.py", label="Dashboard")
        st.page_link("pages/2_Tasks.py", label="Tasks")
        st.divider()

        email = st.session_state.get("email")
        if email:
            st.caption(f"Logged in as {email}")

        if st.button("Logout", use_container_width=True):
            clear_session()
            st.switch_page("app.py")
