
import pandas as pd

from app.services.hospital_analytics import calculate_kpis


def test_kpi_calculations():
    frame = pd.DataFrame(
        {
            "overall_rating": [5, 3, None, 4],
            "emergency_services": [True, False, True, None],
        }
    )

    result = calculate_kpis(frame)

    assert result["hospital_count"] == 4
    assert result["rated_count"] == 3
    assert result["rating_coverage_pct"] == 75.0
    assert result["average_rating"] == 4.0
    assert result["emergency_count"] == 2
    assert result["emergency_coverage_pct"] == 50.0


def test_empty_selection():
    frame = pd.DataFrame(
        columns=["overall_rating", "emergency_services"]
    )

    result = calculate_kpis(frame)

    assert result["hospital_count"] == 0
    assert result["rating_coverage_pct"] is None
    assert result["average_rating"] is None


def test_unrated_hospitals_excluded_from_average():
    frame = pd.DataFrame(
        {
            "overall_rating": [None, None, 5],
            "emergency_services": [False, False, True],
        }
    )

    result = calculate_kpis(frame)

    assert result["rated_count"] == 1
    assert result["average_rating"] == 5.0
    assert result["rating_coverage_pct"] == 33.33
