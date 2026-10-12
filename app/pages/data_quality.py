
import streamlit as st

from app.components.layout import page_header, section_header
from app.services.hospital_analytics import (
    get_data_quality,
    get_pipeline_runs,
)


def render():
    page_header(
        "Data Quality & Pipeline Monitoring",
        "Track source reconciliation, ingestion history "
        "and healthcare data reliability.",
    )

    try:
        quality = get_data_quality()
        runs = get_pipeline_runs()
    except Exception:
        st.error(
            "Unable to load data quality information. "
            "Verify PostgreSQL connectivity and migrations."
        )
        return

    if quality.empty:
        st.warning("No CMS hospital snapshot is available.")
        return

    record = quality.iloc[0]

    if bool(record["reconciled"]):
        st.success(
            "Latest CMS snapshot reconciles across "
            "source, raw and core layers."
        )
    else:
        st.error(
            "Source, raw and core record counts do not match."
        )

    section_header(
        "Snapshot Reconciliation",
        "These counts must match before hospital KPIs "
        "are considered verified.",
    )

    left, middle, right = st.columns(3)

    left.metric(
        "Source rows",
        f"{int(record['source_row_count']):,}",
    )
    middle.metric(
        "Raw rows",
        f"{int(record['raw_rows']):,}",
    )
    right.metric(
        "Core rows",
        f"{int(record['core_rows']):,}",
    )

    with st.container(border=True):
        st.subheader("Snapshot lineage")
        st.write(f"Snapshot ID: {record['snapshot_id']}")
        st.write(f"Downloaded at: {record['downloaded_at']}")
        st.code(str(record["source_sha256"]))

    section_header(
        "Pipeline Execution History",
        "Review completed, failed and duplicate ingestion runs.",
    )

    if runs.empty:
        st.info("No pipeline executions have been recorded.")
    else:
        st.dataframe(
            runs,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("What does reconciliation prove?"):
        st.write(
            "It confirms that source, raw and core record "
            "counts agree for the latest snapshot."
        )
        st.write(
            "It does not independently prove that every "
            "CMS source value is clinically accurate."
        )
