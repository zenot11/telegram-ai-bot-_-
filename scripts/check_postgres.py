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
    fetch_achievements_postgres,
    fetch_directions_postgres,
    fetch_regions_postgres,
    fetch_universities_postgres,
)


REQUIRED_TABLES = ("universities", "directions", "passing_scores", "achievements")


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
            achievements_count = await connection.fetchval("SELECT COUNT(*) FROM achievements")
            synthetic_count = await connection.fetchval(
                """
                SELECT COUNT(*)
                FROM universities
                WHERE name ILIKE '%Региональный центр технологий и инженерии%'
                   OR name ILIKE '%Институт социальных и цифровых профессий%'
                   OR COALESCE(short_name, '') ~* '^(РЦТИ|ИСЦП)-[0-9]+$'
                """
            )
            suspicious_rows = await connection.fetch(
                """
                SELECT id, name, short_name, city, region, website
                FROM universities
                WHERE name ILIKE '%Региональный центр технологий%'
                   OR short_name ILIKE 'РЦТИ%'
                ORDER BY id
                LIMIT 5
                """
            )
            suspicious_join_rows = await connection.fetch(
                """
                SELECT
                  u.id,
                  u.name AS university_name,
                  u.short_name,
                  u.city,
                  u.region,
                  f.name AS faculty_name,
                  d.name AS direction_name,
                  d.profile,
                  d.study_form::TEXT AS study_form,
                  ps.min_score,
                  ps.admission_type::TEXT AS admission_type,
                  ps.note,
                  ps.year
                FROM universities u
                LEFT JOIN faculties f ON f.university_id = u.id
                LEFT JOIN directions d ON d.faculty_id = f.id
                LEFT JOIN passing_scores ps ON ps.direction_id = d.id
                WHERE u.name ILIKE '%Региональный центр технологий%'
                   OR u.short_name ILIKE 'РЦТИ%'
                ORDER BY u.id, d.id, ps.year DESC
                LIMIT 20
                """
            )

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
        default_synthetic_sample = await fetch_universities_postgres(
            pool,
            build_university_filters(
                {
                    "q": "Региональный центр технологий",
                    "limit": "5",
                }
            ),
        )
        include_synthetic_sample = await fetch_universities_postgres(
            pool,
            build_university_filters(
                {
                    "q": "Региональный центр технологий",
                    "limit": "5",
                    "include_synthetic": "true",
                }
            ),
        )
        achievements = await fetch_achievements_postgres(pool, limit=3)
    except Exception:
        print("PostgreSQL check failed: connection or query failed. Check DATABASE_URL, schema and seed data.")
        return 1
    finally:
        if pool is not None:
            await pool.close()

    print("PostgreSQL check passed.")
    print(f"Universities: {universities_count}")
    print(f"Synthetic universities: {synthetic_count}")
    print(f"Suspicious university rows: {len(suspicious_rows)}")
    for row in suspicious_rows[:3]:
        print(f"  - #{row['id']}: {row['name']} / {row['short_name']} / {row['region']}")
    print(f"Suspicious join sample rows: {len(suspicious_join_rows)}")
    print(f"Default API excludes synthetic records: {'yes' if not default_synthetic_sample else 'no'}")
    print(f"include_synthetic works: {'yes' if include_synthetic_sample else 'no'}")
    print(f"Regions: {len(regions)}")
    print(f"Directions: {directions_count}")
    print(f"Directory directions: {len(directions)}")
    print(f"Passing scores: {scores_count}")
    print(f"Achievements: {achievements_count}")
    print(f"Sample /api/universities-like rows: {len(sample)}")
    print(f"Sample achievements rows: {len(achievements)}")
    if sample:
        first = sample[0]
        print(
            "Display labels: "
            f"financing_label={first.get('financing_label', '') or 'empty'}, "
            f"contest_label={first.get('contest_label', '') or 'empty'}, "
            f"study_form_label={first.get('study_form_label', '') or 'empty'}"
        )
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
