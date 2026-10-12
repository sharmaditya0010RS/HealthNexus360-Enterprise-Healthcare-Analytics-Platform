
import json

from sqlalchemy import text

from database.connection import get_engine
from pipelines.ingestion.cms_hospitals import (
    CMS_DATASET_URL,
    download_hospital_dataset,
)
from pipelines.validation.hospital_quality import (
    validate_hospitals,
)


def create_pipeline_run(connection):
    return connection.execute(
        text(
            "INSERT INTO audit.pipeline_runs "
            "(pipeline_name, source_name, status) "
            "VALUES ('cms_hospital_ingestion', "
            "'CMS Hospital General Information', 'running') "
            "RETURNING run_id"
        )
    ).scalar_one()


def update_pipeline_run(
    connection,
    run_id,
    status,
    records_read,
    records_loaded,
    error_message=None,
):
    connection.execute(
        text(
            "UPDATE audit.pipeline_runs SET "
            "status = :status, "
            "finished_at = NOW(), "
            "records_read = :records_read, "
            "records_loaded = :records_loaded, "
            "error_message = :error_message "
            "WHERE run_id = :run_id"
        ),
        {
            "run_id": run_id,
            "status": status,
            "records_read": records_read,
            "records_loaded": records_loaded,
            "error_message": error_message,
        },
    )


def main():
    engine = get_engine()

    with engine.begin() as connection:
        run_id = create_pipeline_run(connection)

    records_read = 0

    try:
        dataset = download_hospital_dataset()
        records_read = len(dataset.records)

        quality = validate_hospitals(dataset.records)

        if quality.rejected_rows:
            sample = quality.rejected_rows[:5]
            raise ValueError(
                f"{len(quality.rejected_rows)} rejected rows: "
                f"{sample}"
            )

        with engine.begin() as connection:
            existing_snapshot = connection.execute(
                text(
                    "SELECT snapshot_id "
                    "FROM raw.cms_hospital_snapshots "
                    "WHERE source_sha256 = :sha256"
                ),
                {"sha256": dataset.sha256},
            ).scalar_one_or_none()

            if existing_snapshot is not None:
                update_pipeline_run(
                    connection,
                    run_id,
                    "success",
                    records_read,
                    0,
                )
                print(
                    "Snapshot already loaded:",
                    existing_snapshot,
                )
                return

            snapshot_id = connection.execute(
                text(
                    "INSERT INTO raw.cms_hospital_snapshots "
                    "(source_url, source_sha256, "
                    "source_row_count, source_column_count) "
                    "VALUES (:source_url, :sha256, "
                    ":row_count, :column_count) "
                    "RETURNING snapshot_id"
                ),
                {
                    "source_url": CMS_DATASET_URL,
                    "sha256": dataset.sha256,
                    "row_count": records_read,
                    "column_count": dataset.column_count,
                },
            ).scalar_one()

            raw_rows = [
                {
                    "snapshot_id": snapshot_id,
                    "row_number": index,
                    "record": json.dumps(record),
                }
                for index, record in enumerate(
                    dataset.records,
                    start=1,
                )
            ]

            connection.execute(
                text(
                    "INSERT INTO raw.cms_hospital_records "
                    "(snapshot_id, row_number, record) "
                    "VALUES (:snapshot_id, :row_number, "
                    "CAST(:record AS JSONB))"
                ),
                raw_rows,
            )

            hospital_rows = [
                {"snapshot_id": snapshot_id, **hospital}
                for hospital in quality.hospitals
            ]

            connection.execute(
                text(
                    "INSERT INTO core.hospitals ("
                    "snapshot_id, facility_id, facility_name, "
                    "state, city, zip_code, hospital_type, "
                    "hospital_ownership, emergency_services, "
                    "overall_rating) VALUES ("
                    ":snapshot_id, :facility_id, "
                    ":facility_name, :state, :city, "
                    ":zip_code, :hospital_type, "
                    ":hospital_ownership, "
                    ":emergency_services, :overall_rating)"
                ),
                hospital_rows,
            )

            update_pipeline_run(
                connection,
                run_id,
                "success",
                records_read,
                len(hospital_rows),
            )

        print("CMS hospital ingestion completed.")
        print("Snapshot ID:", snapshot_id)
        print("Source records:", records_read)
        print("Loaded hospitals:", len(hospital_rows))
        print("SHA-256:", dataset.sha256)

    except Exception as error:
        with engine.begin() as connection:
            update_pipeline_run(
                connection,
                run_id,
                "failed",
                records_read,
                0,
                str(error)[:4000],
            )

        raise


if __name__ == "__main__":
    main()
