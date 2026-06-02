# -*- coding: utf-8 -*-
"""Standalone entrypoint for the Fan Pulse dashboard."""

from pathlib import Path
import sys

import streamlit as st


APP_DIRECTORY = Path(__file__).resolve().parent.parent
if str(APP_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(APP_DIRECTORY))

from analytics import show_pulse  # noqa: E402


st.set_page_config(
    page_title="F1 PULSE - The Voice of the Fans",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

show_pulse()
