"""Streamlit session-state helpers for auth state and backend configuration."""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")


def is_authenticated() -> bool:
    return "access_token" in st.session_state


def set_session(access_token: str, user_id: str, email: str) -> None:
    st.session_state["access_token"] = access_token
    st.session_state["user_id"] = user_id
    st.session_state["email"] = email


def clear_session() -> None:
    st.session_state.clear()


def require_auth() -> None:
    """Call as the first line of any page that requires a logged-in user."""
    if not is_authenticated():
        st.warning("Please log in first.")
        st.switch_page("app.py")
        st.stop()
