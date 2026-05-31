import os
from typing import Any


TRUE_VALUES = {"1", "true", "yes", "on"}


class PostgresConfigError(RuntimeError):
    """Raised when PostgreSQL mode is enabled but cannot be initialized."""


def is_postgres_enabled() -> bool:
    return os.getenv("USE_POSTGRES", "").strip().lower() in TRUE_VALUES


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "").strip()


async def create_pool() -> Any:
    database_url = get_database_url()
    if not database_url:
        raise PostgresConfigError("DATABASE_URL is required when USE_POSTGRES=true")

    try:
        import asyncpg
    except ImportError as error:
        raise PostgresConfigError("asyncpg is required when USE_POSTGRES=true") from error

    try:
        pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=1,
            max_size=5,
            command_timeout=10,
        )
        async with pool.acquire() as connection:
            await connection.execute("SELECT 1")
    except Exception as error:
        raise PostgresConfigError("could not connect to PostgreSQL; check DATABASE_URL and database availability") from error

    return pool


async def close_pool(pool: Any | None) -> None:
    if pool is not None:
        await pool.close()
