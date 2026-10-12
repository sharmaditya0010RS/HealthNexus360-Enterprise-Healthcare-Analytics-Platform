
import csv
import hashlib
import io
import re
from dataclasses import dataclass

import requests

CMS_DATASET_URL = (
    "https://data.cms.gov/provider-data/dataset/xubh-q36u"
)

CMS_DOWNLOAD_URL = (
    "https://data.cms.gov/provider-data/api/1/datastore/"
    "query/xubh-q36u/0/download?format=csv"
)

REQUIRED_COLUMNS = {
    "facility_id",
    "facility_name",
    "state",
    "citytown",
    "zip_code",
    "hospital_type",
    "hospital_ownership",
    "emergency_services",
    "hospital_overall_rating",
}


@dataclass
class HospitalDataset:
    records: list[dict[str, str]]
    sha256: str
    column_count: int



def normalize_column_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    normalized = name.strip("_")

    aliases = {
        "city_town": "citytown",
    }

    return aliases.get(normalized, normalized)



def parse_hospital_csv(content: bytes) -> HospitalDataset:
    digest = hashlib.sha256(content).hexdigest()

    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(
            "CMS response is not valid UTF-8 CSV."
        ) from error

    reader = csv.DictReader(io.StringIO(decoded))

    original_columns = reader.fieldnames

    if not original_columns:
        raise ValueError("CMS CSV has no header.")

    normalized_columns = [
        normalize_column_name(column)
        for column in original_columns
    ]

    if len(normalized_columns) != len(
        set(normalized_columns)
    ):
        raise ValueError(
            "CMS CSV has duplicate normalized columns."
        )

    missing = REQUIRED_COLUMNS - set(normalized_columns)

    if missing:
        raise ValueError(
            "CMS CSV missing required columns: "
            f"{sorted(missing)}. "
            f"Received columns: {original_columns[:12]}"
        )

    records = []

    for row in reader:
        if None in row:
            raise ValueError(
                "CMS CSV contains a malformed row."
            )

        normalized_record = {
            normalize_column_name(key): value
            for key, value in row.items()
        }

        records.append(normalized_record)

    if not records:
        raise ValueError(
            "CMS CSV contains no hospital records."
        )

    return HospitalDataset(
        records=records,
        sha256=digest,
        column_count=len(original_columns),
    )


def download_hospital_dataset() -> HospitalDataset:
    response = requests.get(
        CMS_DOWNLOAD_URL,
        timeout=(15, 120),
        headers={"Accept": "text/csv"},
    )

    response.raise_for_status()

    return parse_hospital_csv(response.content)
