
import streamlit as st

from app.pages import control_center, home
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
    st.caption("Healthcare Decision Intelligence")
    st.divider()

    selected_page = st.radio(
        "Workspace",
        options=[
            "Executive Overview",
            "Control Center",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Environment")
    st.write(settings.app_env.title())
    st.caption("Phase 0 — Foundation")

if selected_page == "Executive Overview":
    home.render()

elif selected_page == "Control Center":
    control_center.render()
