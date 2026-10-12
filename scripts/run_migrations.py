
from pathlib import Path

from sqlalchemy import text

from database.connection import get_engine

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "database" / "migrations"


def run_migrations() -> None:
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE SCHEMA IF NOT EXISTS governance"
            )
        )
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS "
                "governance.schema_migrations ("
                "version VARCHAR(100) PRIMARY KEY, "
                "applied_at TIMESTAMPTZ NOT NULL "
                "DEFAULT NOW())"
            )
        )

    for migration in sorted(MIGRATIONS.glob("*.sql")):
        with engine.begin() as connection:
            exists = connection.execute(
                text(
                    "SELECT 1 FROM "
                    "governance.schema_migrations "
                    "WHERE version = :version"
                ),
                {"version": migration.name},
            ).scalar_one_or_none()

            if exists is not None:
                print(f"SKIPPED: {migration.name}")
                continue

            sql = migration.read_text(encoding="utf-8")

            connection.exec_driver_sql(sql)

            connection.execute(
                text(
                    "INSERT INTO "
                    "governance.schema_migrations (version) "
                    "VALUES (:version)"
                ),
                {"version": migration.name},
            )

            print(f"APPLIED: {migration.name}")


if __name__ == "__main__":
    run_migrations()
