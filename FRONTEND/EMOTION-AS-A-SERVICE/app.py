import streamlit as st

from analytics import show_analytics
from grid_positioning import show_grid_positioning

st.set_page_config(
    page_title="F1 Predictor",
    layout="wide"
)

st.sidebar.markdown("## 🧭 Navigation")

page = st.sidebar.radio(
    "Go to:",
    ["Podium Simulator", "Red Bull Analytics"]
)

st.sidebar.markdown("---")

if page == "Podium Simulator":
    show_grid_positioning()

elif page == "Red Bull Analytics":
    show_analytics()