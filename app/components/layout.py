
import streamlit as st


def page_header(
    title: str,
    description: str,
) -> None:
    st.title(title)
    st.write(description)
    st.divider()


def section_header(
    title: str,
    description: str,
) -> None:
    st.subheader(title)
    st.caption(description)


def information_panel(
    title: str,
    message: str,
) -> None:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(message)
