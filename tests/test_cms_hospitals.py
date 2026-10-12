
import pytest

from pipelines.ingestion.cms_hospitals import (
    parse_hospital_csv,
)
from pipelines.validation.hospital_quality import (
    parse_emergency,
    parse_rating,
    validate_hospitals,
)


def sample_record():
    return {
        "facility_id": "010001",
        "facility_name": "Example Hospital",
        "state": "AL",
        "citytown": "Example City",
        "zip_code": "01234",
        "hospital_type": "Acute Care Hospitals",
        "hospital_ownership": "Government",
        "emergency_services": "Yes",
        "hospital_overall_rating": "4",
    }


def test_hospital_validation():
    result = validate_hospitals([sample_record()])

    assert result.total_rows == 1
    assert len(result.hospitals) == 1
    assert not result.rejected_rows
    assert result.hospitals[0]["facility_id"] == "010001"
    assert result.hospitals[0]["zip_code"] == "01234"
    assert result.hospitals[0]["overall_rating"] == 4


def test_missing_rating_is_not_zero():
    record = sample_record()
    record["hospital_overall_rating"] = "Not Available"

    result = validate_hospitals([record])

    assert result.hospitals[0]["overall_rating"] is None


def test_duplicate_hospital_is_rejected():
    record = sample_record()
    result = validate_hospitals([record, record.copy()])

    assert len(result.hospitals) == 1
    assert len(result.rejected_rows) == 1


def test_invalid_rating():
    with pytest.raises(ValueError):
        parse_rating("9")


def test_emergency_services():
    assert parse_emergency("Yes") is True
    assert parse_emergency("No") is False
    assert parse_emergency("Not Available") is None


def test_csv_missing_required_columns():
    content = b"facility_id,facility_name\n010001,Example\n"

    with pytest.raises(ValueError):
        parse_hospital_csv(content)


def test_cms_display_name_headers():
    headers = (
        "Facility ID,Facility Name,State,City/Town,"
        "ZIP Code,Hospital Type,Hospital Ownership,"
        "Emergency Services,Hospital overall rating"
    )

    row = (
        "010001,Example Hospital,AL,Example City,"
        "01234,Acute Care Hospitals,Government,Yes,4"
    )

    content = f"{headers}\n{row}\n".encode("utf-8")

    dataset = parse_hospital_csv(content)

    assert len(dataset.records) == 1
    assert dataset.records[0]["facility_id"] == "010001"
    assert dataset.records[0]["citytown"] == "Example City"
    assert dataset.records[0]["zip_code"] == "01234"
    assert dataset.records[0]["hospital_overall_rating"] == "4"

