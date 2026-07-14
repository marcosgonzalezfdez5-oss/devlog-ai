"""Task Manager - Streamlit entrypoint: login page."""

import streamlit as st

from services import auth_service
from services.api_client import ApiError
from utils.session import is_authenticated, set_session

st.set_page_config(page_title="Task Manager", page_icon="\U0001F4CB", layout="centered")

if is_authenticated():
    st.switch_page("pages/1_Dashboard.py")

st.title("Task Manager")
st.subheader("Log in")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log in")

if submitted:
    try:
        result = auth_service.login(email, password)
    except ApiError as exc:
        st.error(exc.message)
    else:
        set_session(result["access_token"], result["user_id"], result["email"])
        st.switch_page("pages/1_Dashboard.py")
