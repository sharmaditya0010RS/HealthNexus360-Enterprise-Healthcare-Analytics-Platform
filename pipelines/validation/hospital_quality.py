
from dataclasses import dataclass

MISSING_VALUES = {
    "",
    "not available",
    "n/a",
    "na",
    "null",
}


@dataclass
class QualityResult:
    hospitals: list[dict]
    rejected_rows: list[dict]
    total_rows: int


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    if cleaned.lower() in MISSING_VALUES:
        return None

    return cleaned


def parse_rating(value: str | None) -> int | None:
    cleaned = clean_text(value)

    if cleaned is None:
        return None

    if cleaned not in {"1", "2", "3", "4", "5"}:
        raise ValueError(f"Invalid rating: {cleaned}")

    return int(cleaned)


def parse_emergency(value: str | None) -> bool | None:
    cleaned = clean_text(value)

    if cleaned is None:
        return None

    normalized = cleaned.lower()

    if normalized == "yes":
        return True

    if normalized == "no":
        return False

    raise ValueError(f"Invalid emergency flag: {cleaned}")


def validate_hospitals(records: list[dict]) -> QualityResult:
    hospitals = []
    rejected = []
    seen_ids = set()

    for row_number, record in enumerate(records, start=1):
        try:
            facility_id = clean_text(record["facility_id"])
            name = clean_text(record["facility_name"])
            state = clean_text(record["state"])

            if not facility_id or not name or not state:
                raise ValueError("Missing required hospital identity")

            if facility_id in seen_ids:
                raise ValueError("Duplicate facility ID")

            hospital = {
                "facility_id": facility_id,
                "facility_name": name,
                "state": state.upper(),
                "city": clean_text(record["citytown"]),
                "zip_code": clean_text(record["zip_code"]),
                "hospital_type": clean_text(
                    record["hospital_type"]
                ),
                "hospital_ownership": clean_text(
                    record["hospital_ownership"]
                ),
                "emergency_services": parse_emergency(
                    record["emergency_services"]
                ),
                "overall_rating": parse_rating(
                    record["hospital_overall_rating"]
                ),
            }

            seen_ids.add(facility_id)
            hospitals.append(hospital)

        except (ValueError, KeyError, TypeError) as error:
            rejected.append(
                {
                    "row_number": row_number,
                    "facility_id": record.get("facility_id"),
                    "reason": str(error),
                }
            )

    return QualityResult(
        hospitals=hospitals,
        rejected_rows=rejected,
        total_rows=len(records),
    )
