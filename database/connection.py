
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()

    if not settings.database_url:
        raise ValueError(
            "DATABASE_URL is missing from the environment."
        )

    if not settings.database_url.startswith(
        "postgresql+psycopg://"
    ):
        raise ValueError(
            "DATABASE_URL must use the postgresql+psycopg driver."
        )

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
        pool_recycle=1800,
        connect_args={"connect_timeout": 10},
    )


def check_database_connection() -> dict:
    with get_engine().connect() as connection:
        result = connection.execute(
            text(
                "SELECT current_database(), "
                "current_user, version()"
            )
        ).one()

    return {
        "database": result[0],
        "user": result[1],
        "version": result[2].split(",")[0],
        "status": "connected",
    }
