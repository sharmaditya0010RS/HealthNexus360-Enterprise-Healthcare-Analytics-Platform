
import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.layout import page_header, section_header
from app.services.hospital_analytics import (
    calculate_kpis,
    get_hospitals,
)


@st.cache_data(ttl=300, show_spinner=False)
def load_hospitals() -> pd.DataFrame:
    return get_hospitals()


def format_percent(value):
    return "N/A" if value is None else f"{value:.1f}%"


def format_rating(value):
    return "N/A" if value is None else f"{value:.2f} / 5"


def render():
    page_header(
        "Hospital Performance Intelligence",
        "Explore official CMS hospital records with "
        "transparent metrics and interactive comparisons.",
    )

    try:
        hospitals = load_hospitals()
    except Exception:
        st.error(
            "Hospital data could not be loaded. "
            "Check the database connection and migrations."
        )
        return

    if hospitals.empty:
        st.warning(
            "No hospitals found. Run the CMS ingestion pipeline."
        )
        return

    with st.container(border=True):
        st.subheader("Explore the hospital network")

        states = sorted(
            hospitals["state"].dropna().unique().tolist()
        )
        hospital_types = sorted(
            hospitals["hospital_type"]
            .dropna()
            .unique()
            .tolist()
        )

        left, right = st.columns(2)

        with left:
            selected_states = st.multiselect(
                "State or territory",
                options=states,
                placeholder="All states and territories",
            )

        with right:
            selected_types = st.multiselect(
                "Hospital type",
                options=hospital_types,
                placeholder="All hospital types",
            )

    filtered = hospitals.copy()

    if selected_states:
        filtered = filtered[
            filtered["state"].isin(selected_states)
        ]

    if selected_types:
        filtered = filtered[
            filtered["hospital_type"].isin(selected_types)
        ]

    kpis = calculate_kpis(filtered)

    if filtered.empty:
        st.info("No hospitals match the selected filters.")
        return

    section_header(
        "Executive KPI Scorecard",
        "All metrics reflect the selected hospitals.",
    )

    columns = st.columns(4)

    columns[0].metric(
        "Hospitals",
        f"{kpis['hospital_count']:,}",
        help="Number of CMS hospital records in the selection.",
    )

    columns[1].metric(
        "Rating coverage",
        format_percent(kpis["rating_coverage_pct"]),
        help="Rated hospitals divided by all selected hospitals.",
    )

    columns[2].metric(
        "Average reported rating",
        format_rating(kpis["average_rating"]),
        help="Simple average of available CMS overall ratings.",
    )

    columns[3].metric(
        "Emergency service availability",
        format_percent(kpis["emergency_coverage_pct"]),
        help="Hospitals marked Yes for emergency services "
        "divided by all selected hospitals.",
    )

    section_header(
        "Hospital Rating Distribution",
        "Missing ratings are shown separately.",
    )

    rating_labels = (
        pd.to_numeric(
            filtered["overall_rating"],
            errors="coerce",
        )
        .apply(
            lambda value: (
                "Unrated"
                if pd.isna(value)
                else f"{int(value)} star"
            )
        )
    )

    rating_order = [
        "1 star",
        "2 star",
        "3 star",
        "4 star",
        "5 star",
        "Unrated",
    ]

    distribution = (
        rating_labels.value_counts()
        .reindex(rating_order, fill_value=0)
        .rename_axis("Rating")
        .reset_index(name="Hospitals")
    )

    figure = px.bar(
        distribution,
        x="Rating",
        y="Hospitals",
        text="Hospitals",
        color="Hospitals",
        color_continuous_scale="Teal",
    )
    figure.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(figure, use_container_width=True)

    section_header(
        "Geographic Comparison",
        "Compare rating availability across states "
        "and territories.",
    )

    state_summary = (
        filtered.groupby("state", dropna=False)
        .agg(
            hospitals=("facility_id", "count"),
            rated=("overall_rating", "count"),
            average_rating=("overall_rating", "mean"),
        )
        .reset_index()
    )

    state_summary["rating_coverage_pct"] = (
        100
        * state_summary["rated"]
        / state_summary["hospitals"]
    ).round(2)

    state_summary["average_rating"] = (
        state_summary["average_rating"].round(2)
    )

    state_summary = state_summary.sort_values(
        ["hospitals", "state"],
        ascending=[False, True],
    )

    st.dataframe(
        state_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "state": "State",
            "hospitals": "Hospitals",
            "rated": "Rated hospitals",
            "average_rating": "Average rating",
            "rating_coverage_pct": st.column_config
            .ProgressColumn(
                "Rating coverage %",
                min_value=0,
                max_value=100,
                format="%.1f%%",
            ),
        },
    )

    section_header(
        "Hospital Explorer",
        "Inspect individual facility records and export "
        "the filtered selection.",
    )

    search = st.text_input(
        "Search hospital name or facility ID",
        placeholder="Enter a hospital name or CMS ID",
    ).strip()

    explorer = filtered.copy()

    if search:
        mask = (
            explorer["facility_name"]
            .fillna("")
            .str.contains(search, case=False, regex=False)
            | explorer["facility_id"]
            .fillna("")
            .str.contains(search, case=False, regex=False)
        )
        explorer = explorer[mask]

    st.dataframe(
        explorer,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download filtered hospital data (CSV)",
        data=explorer.to_csv(index=False).encode("utf-8"),
        file_name="healthnexus_hospitals.csv",
        mime="text/csv",
    )

    with st.expander("How to interpret these metrics"):
        st.write(
            "CMS overall ratings are facility-level summary "
            "measures. A missing rating is not a zero-star rating."
        )
        st.write(
            "Average ratings are unweighted descriptive "
            "statistics and should not be interpreted as "
            "risk-adjusted clinical outcomes."
        )
        st.write(
            "State comparisons may be influenced by differences "
            "in hospital composition and rating availability."
        )
