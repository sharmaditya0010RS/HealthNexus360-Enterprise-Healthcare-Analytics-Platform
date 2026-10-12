
from sqlalchemy import text

from database.connection import get_engine


def main():
    engine = get_engine()

    with engine.connect() as connection:
        summary = connection.execute(
            text(
                "SELECT snapshot_id, hospital_count, "
                "rated_hospitals, state_count, "
                "emergency_service_hospitals, average_rating "
                "FROM mart.hospital_overview"
            )
        ).mappings().first()

        if summary is None:
            raise RuntimeError(
                "No CMS hospital snapshot has been loaded."
            )

        snapshot_id = summary["snapshot_id"]

        raw_count = connection.execute(
            text(
                "SELECT COUNT(*) "
                "FROM raw.cms_hospital_records "
                "WHERE snapshot_id = :snapshot_id"
            ),
            {"snapshot_id": snapshot_id},
        ).scalar_one()

        source_count = connection.execute(
            text(
                "SELECT source_row_count "
                "FROM raw.cms_hospital_snapshots "
                "WHERE snapshot_id = :snapshot_id"
            ),
            {"snapshot_id": snapshot_id},
        ).scalar_one()

        print("Latest snapshot:", snapshot_id)
        print("Source records:", source_count)
        print("Raw records:", raw_count)

        for key, value in summary.items():
            print(f"{key}: {value}")

        if not (
            source_count
            == raw_count
            == summary["hospital_count"]
        ):
            raise RuntimeError(
                "CMS source/raw/core reconciliation failed."
            )

        rating_rows = connection.execute(
            text(
                "SELECT overall_rating, COUNT(*) AS hospitals "
                "FROM core.hospitals "
                "WHERE snapshot_id = :snapshot_id "
                "GROUP BY overall_rating "
                "ORDER BY overall_rating NULLS LAST"
            ),
            {"snapshot_id": snapshot_id},
        ).all()

        print("Rating distribution:")

        for rating, count in rating_rows:
            label = rating if rating is not None else "Unrated"
            print(f"  {label}: {count}")

        print("RECONCILIATION PASSED")


if __name__ == "__main__":
    main()
