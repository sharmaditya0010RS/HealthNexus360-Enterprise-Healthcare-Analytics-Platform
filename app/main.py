
import streamlit as st

from app.pages import (
    control_center,
    data_quality,
    home,
    hospital_performance,
)
from app.styles.theme import load_theme
from config.settings import get_settings

st.set_page_config(
    page_title="HealthNexus 360",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_theme()

settings = get_settings()

with st.sidebar:
    st.title("HealthNexus 360")
    st.caption("Enterprise Healthcare Intelligence")

    selected_page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Hospital Performance",
            "Data Quality",
            "Control Center",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(f"Environment: {settings.app_env}")

if selected_page == "Executive Overview":
    home.render()
elif selected_page == "Hospital Performance":
    hospital_performance.render()
elif selected_page == "Data Quality":
    data_quality.render()
else:
    control_center.render()
