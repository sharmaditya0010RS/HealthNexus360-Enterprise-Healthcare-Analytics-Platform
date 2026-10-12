
from pathlib import Path

import streamlit as st

from app.components.layout import (
    page_header,
    section_header,
)

ROOT = Path(__file__).resolve().parents[2]

REPORT_DIRECTORIES = {
    "PDF": ROOT / "reports" / "outputs",
    "Excel": ROOT / "reports" / "outputs",
    "PowerPoint": ROOT / "presentations",
}

EXTENSIONS = {
    "PDF": ".pdf",
    "Excel": ".xlsx",
    "PowerPoint": ".pptx",
}

MIME_TYPES = {
    ".pdf": "application/pdf",
    ".xlsx": (
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    ".pptx": (
        "application/vnd.openxmlformats-officedocument."
        "presentationml.presentation"
    ),
}


def available_reports(
    report_type: str,
) -> list[Path]:
    directory = REPORT_DIRECTORIES[report_type]

    if not directory.exists():
        return []

    return sorted(
        directory.glob(f"*{EXTENSIONS[report_type]}"),
        key=lambda path: path.name,
    )


def render_report_group(report_type: str) -> None:
    files = available_reports(report_type)

    with st.container(border=True):
        st.subheader(f"{report_type} Reports")

        if not files:
            st.caption(
                "No generated reports are available yet."
            )
            return

        for file_path in files:
            st.download_button(
                label=f"Download {file_path.name}",
                data=file_path.read_bytes(),
                file_name=file_path.name,
                mime=MIME_TYPES[file_path.suffix],
                key=f"download_{report_type}_{file_path.name}",
                width="stretch",
            )


def render() -> None:
    page_header(
        "Executive Control Center",
        "Access analytical modules, generated "
        "reports, and business documentation "
        "from one central workspace.",
    )

    section_header(
        "Report Library",
        "Only successfully generated reports "
        "are available for download.",
    )

    for report_type in REPORT_DIRECTORIES:
        render_report_group(report_type)

    st.divider()

    section_header(
        "Power BI Reporting",
        "Access enterprise BI reports "
        "and their supporting documentation.",
    )

    st.info(
        "Power BI publishing has not been "
        "configured. Report links and validated "
        "artifacts will be connected during "
        "the BI implementation phase."
    )

    st.divider()

    section_header(
        "Project Documentation",
        "Business requirements, functional "
        "specifications, KPI definitions, "
        "and technical architecture.",
    )

    documentation = {
        "Business Requirements": ROOT / "docs" / "brd",
        "Functional Requirements": ROOT / "docs" / "frd",
        "KPI Dictionary": ROOT / "docs" / "kpi_catalog",
        "Architecture": ROOT / "docs" / "architecture",
    }

    for name, directory in documentation.items():
        with st.expander(name):
            documents = (
                sorted(directory.glob("*.md"))
                if directory.exists()
                else []
            )

            if not documents:
                st.caption("Documentation pending.")
                continue

            for document in documents:
                st.download_button(
                    label=f"Download {document.name}",
                    data=document.read_bytes(),
                    file_name=document.name,
                    mime="text/markdown",
                    key=f"doc_{name}_{document.name}",
                )
