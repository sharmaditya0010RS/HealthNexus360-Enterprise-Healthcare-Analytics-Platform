
from pathlib import Path

import streamlit as st


def load_theme() -> None:
    css_path = Path(__file__).with_name("main.css")
    css = css_path.read_text(encoding="utf-8")
    st.html(f"<style>{css}</style>")
