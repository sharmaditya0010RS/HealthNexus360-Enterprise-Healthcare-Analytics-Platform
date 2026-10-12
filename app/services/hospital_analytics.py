
import pandas as pd
from sqlalchemy import text

from database.connection import get_engine


def query_frame(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as connection:
        return pd.read_sql_query(
            text(sql),
            connection,
            params=params or {},
        )


def get_states() -> list[str]:
    frame = query_frame(
        "SELECT DISTINCT state "
        "FROM mart.hospital_latest ORDER BY state"
    )
    return frame["state"].tolist()


def get_hospitals(
    states: list[str] | None = None,
    hospital_types: list[str] | None = None,
) -> pd.DataFrame:
    return query_frame(
        """
        SELECT
            facility_id,
            facility_name,
            state,
            city,
            hospital_type,
            hospital_ownership,
            emergency_services,
            overall_rating
        FROM mart.hospital_latest
        WHERE (
            :all_states
            OR state = ANY(:states)
        )
        AND (
            :all_types
            OR hospital_type = ANY(:hospital_types)
        )
        ORDER BY state, facility_name, facility_id
        """,
        {
            "all_states": not bool(states),
            "states": states or [],
            "all_types": not bool(hospital_types),
            "hospital_types": hospital_types or [],
        },
    )


def calculate_kpis(frame: pd.DataFrame) -> dict:
    count = len(frame)

    if count == 0:
        return {
            "hospital_count": 0,
            "rated_count": 0,
            "rating_coverage_pct": None,
            "average_rating": None,
            "emergency_count": 0,
            "emergency_coverage_pct": None,
        }

    ratings = pd.to_numeric(
        frame["overall_rating"],
        errors="coerce",
    )

    rated_count = int(ratings.notna().sum())
    emergency_count = int(
        frame["emergency_services"].eq(True).sum()
    )

    return {
        "hospital_count": count,
        "rated_count": rated_count,
        "rating_coverage_pct": round(
            100 * rated_count / count,
            2,
        ),
        "average_rating": (
            round(float(ratings.mean()), 2)
            if rated_count
            else None
        ),
        "emergency_count": emergency_count,
        "emergency_coverage_pct": round(
            100 * emergency_count / count,
            2,
        ),
    }


def get_data_quality() -> pd.DataFrame:
    return query_frame(
        "SELECT * FROM mart.hospital_data_quality"
    )


def get_pipeline_runs(limit: int = 20) -> pd.DataFrame:
    return query_frame(
        """
        SELECT
            run_id,
            pipeline_name,
            source_name,
            started_at,
            finished_at,
            status,
            records_read,
            records_loaded,
            error_message
        FROM audit.pipeline_runs
        ORDER BY started_at DESC, run_id DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )
