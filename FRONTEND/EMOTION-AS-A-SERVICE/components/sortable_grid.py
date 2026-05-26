import streamlit as st
from streamlit_sortables import sort_items

def show_sortable_grid(driver_abbrs):

    st.subheader("🏎️ Starting Grid")
    st.markdown("Drag drivers to change the starting grid.")

    st.markdown("""
    <style>
    [data-testid="stVerticalBlock"] div div div ul {
        padding: 0;
    }

    [data-testid="stVerticalBlock"] div div div li {
        list-style-type: none;
        background: linear-gradient(90deg, #15151E 0%, #1E1EAA 100%);
        color: white;
        padding: 20px;
        margin-bottom: 12px;
        border-radius: 18px;
        font-size: 30px;
        font-weight: 900;
        text-align: center;
        border-left: 12px solid #FF1801;
        box-shadow: 0 4px 15px rgba(0,0,0,0.35);
        transition: 0.2s ease;
        cursor: grab;
    }

    [data-testid="stVerticalBlock"] div div div li:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

    return sort_items(
        driver_abbrs,
        direction="vertical"
    )