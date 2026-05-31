#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_stub.university_repository import (  # noqa: E402
    build_university_filters,
    fetch_directions_postgres,
    fetch_regions_postgres,
    fetch_universities_postgres,
)


REQUIRED_TABLES = ("universities", "directions", "passing_scores")


async def main_async() -> int:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        print("PostgreSQL check failed: DATABASE_URL is not set.")
        return 1

    try:
        import asyncpg
    except ImportError:
        print("PostgreSQL check failed: asyncpg is not installed.")
        return 1

    pool: Any | None = None
    try:
        pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=2, command_timeout=10)
        async with pool.acquire() as connection:
            tables = await connection.fetch(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = ANY($1::TEXT[])
                ORDER BY table_name
                """,
                list(REQUIRED_TABLES),
            )
            existing_tables = {row["table_name"] for row in tables}
            missing_tables = [table for table in REQUIRED_TABLES if table not in existing_tables]
            if missing_tables:
                print("PostgreSQL check failed: missing tables: " + ", ".join(missing_tables))
                return 1

            universities_count = await connection.fetchval("SELECT COUNT(*) FROM universities")
            directions_count = await connection.fetchval("SELECT COUNT(*) FROM directions")
            scores_count = await connection.fetchval("SELECT COUNT(*) FROM passing_scores")

        regions = await fetch_regions_postgres(pool)
        directions = await fetch_directions_postgres(pool, build_university_filters({}))
        sample = await fetch_universities_postgres(
            pool,
            build_university_filters(
                {
                    "region": "Москва",
                    "score": "260",
                    "direction": "информатика",
                    "type": "budget",
                    "limit": "3",
                    "sort": "min_score_asc",
                }
            ),
        )
    except Exception:
        print("PostgreSQL check failed: connection or query failed. Check DATABASE_URL, schema and seed data.")
        return 1
    finally:
        if pool is not None:
            await pool.close()

    print("PostgreSQL check passed.")
    print(f"Universities: {universities_count}")
    print(f"Regions: {len(regions)}")
    print(f"Directions: {directions_count}")
    print(f"Directory directions: {len(directions)}")
    print(f"Passing scores: {scores_count}")
    print(f"Sample /api/universities-like rows: {len(sample)}")
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
