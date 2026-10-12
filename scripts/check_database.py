
from sqlalchemy import text

from database.connection import (
    check_database_connection,
    get_engine,
)


def main() -> None:
    info = check_database_connection()

    print("Connection status:", info["status"])
    print("Database:", info["database"])
    print("PostgreSQL:", info["version"])

    engine = get_engine()

    with engine.connect() as connection:
        schemas = connection.execute(
            text(
                "SELECT schema_name "
                "FROM information_schema.schemata "
                "WHERE schema_name IN ("
                "'raw', 'staging', 'core', 'mart', "
                "'governance', 'audit', 'insights', "
                "'actions', 'crm', 'ml') "
                "ORDER BY schema_name"
            )
        ).scalars().all()

    print("Project schemas:", ", ".join(schemas))


if __name__ == "__main__":
    main()
