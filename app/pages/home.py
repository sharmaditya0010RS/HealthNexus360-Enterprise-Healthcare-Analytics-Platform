
import streamlit as st

from app.components.layout import (
    information_panel,
    page_header,
    section_header,
)


def render() -> None:
    page_header(
        "Healthcare Intelligence Command Center",
        "A unified platform for hospital performance, "
        "business intelligence, predictive analytics, "
        "and evidence-based decision-making.",
    )

    st.info(
        "Foundation mode: Healthcare datasets have not "
        "been ingested yet. Verified KPIs and analytical "
        "results will appear after the data pipeline "
        "passes validation."
    )

    section_header(
        "Platform capabilities",
        "Explore the business functions available "
        "through the unified analytics workspace.",
    )

    capabilities = [
        (
            "Hospital Performance",
            "Compare hospital quality, spending, "
            "and operational indicators.",
        ),
        (
            "Business Intelligence",
            "Explore validated KPIs, interactive "
            "dashboards, and Power BI reports.",
        ),
        (
            "Predictive Intelligence",
            "Understand forecasts, model performance, "
            "and analytical uncertainty.",
        ),
        (
            "Decision Intelligence",
            "Compare possible business actions "
            "using transparent scenario assumptions.",
        ),
        (
            "Reporting Center",
            "Access analytical reports, business "
            "documents, and executive presentations.",
        ),
        (
            "AI Insight Assistant",
            "Understand verified analytical findings "
            "using simple, stakeholder-friendly language.",
        ),
    ]

    for start in range(0, len(capabilities), 2):
        columns = st.columns(2)

        for column, item in zip(
            columns,
            capabilities[start:start + 2],
        ):
            with column:
                information_panel(item[0], item[1])

    st.divider()

    section_header(
        "How this platform works",
        "Every analytical result follows a "
        "controlled and traceable process.",
    )

    st.write(
        "Data Collection → Data Validation → "
        "Analytics Warehouse → Business Intelligence "
        "→ Recommendations → Executive Reporting"
    )

    st.caption(
        "No demonstration values are presented "
        "as real healthcare findings."
    )
