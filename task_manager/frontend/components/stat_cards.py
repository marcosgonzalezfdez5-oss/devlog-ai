"""Dashboard statistic cards."""

import streamlit as st

_LABELS_AND_KEYS = [
    ("Total Tasks", "total"),
    ("Pending", "pending"),
    ("In Progress", "in_progress"),
    ("Review", "review"),
    ("Completed", "completed"),
]


def render_stat_cards(stats: dict) -> None:
    columns = st.columns(len(_LABELS_AND_KEYS))
    for column, (label, key) in zip(columns, _LABELS_AND_KEYS):
        column.metric(label, stats[key])
