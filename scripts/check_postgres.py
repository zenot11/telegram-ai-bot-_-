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
    direction_code_terms,
    fetch_achievements_postgres,
    fetch_directions_postgres,
    fetch_regions_postgres,
    fetch_universities_postgres,
)
from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN  # noqa: E402


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
                LEFT JOIN directions d ON d.university_id = u.id
                LEFT JOIN faculties f ON f.id = d.faculty_id
                LEFT JOIN passing_scores ps ON ps.direction_id = d.id
                WHERE u.name ILIKE '%Региональный центр технологий%'
                   OR u.short_name ILIKE 'РЦТИ%'
                ORDER BY u.id, d.id, ps.year DESC
                LIMIT 20
                """
            )
            moscow_diagnostics = await connection.fetchrow(
                """
                WITH backend_rows AS (
                    SELECT
                      u.name AS university_name,
                      u.short_name,
                      u.city,
                      u.region,
                      d.code,
                      d.name AS direction_name,
                      d.profile,
                      d.study_form::TEXT AS study_form,
                      ps.admission_type::TEXT AS admission_type,
                      ps.min_score,
                      ps.year
                    FROM passing_scores ps
                    JOIN directions d ON d.id = ps.direction_id
                    JOIN universities u ON u.id = d.university_id
                    WHERE NOT (
                      u.name ILIKE '%Региональный центр технологий и инженерии%'
                      OR u.name ILIKE '%Институт социальных и цифровых профессий%'
                      OR COALESCE(u.short_name, '') ~* '^(РЦТИ|ИСЦП)-[0-9]+$'
                    )
                )
                SELECT
                  COUNT(*) FILTER (
                    WHERE region ILIKE '%Москва%' OR city ILIKE '%Москва%'
                  ) AS moscow_all_count,
                  COUNT(*) FILTER (
                    WHERE (region ILIKE '%Москва%' OR city ILIKE '%Москва%')
                      AND (
                        direction_name ILIKE '%Программная инженерия%'
                        OR COALESCE(profile, '') ILIKE '%Программная инженерия%'
                        OR COALESCE(code, '') = '09.03.04'
                      )
                  ) AS moscow_software_count,
                  COUNT(*) FILTER (
                    WHERE (region ILIKE '%Москва%' OR city ILIKE '%Москва%')
                      AND (
                        direction_name ILIKE '%Программная инженерия%'
                        OR COALESCE(profile, '') ILIKE '%Программная инженерия%'
                        OR COALESCE(code, '') = '09.03.04'
                      )
                      AND study_form = 'part_time'
                  ) AS moscow_software_part_time_count,
                  COUNT(*) FILTER (
                    WHERE (region ILIKE '%Москва%' OR city ILIKE '%Москва%')
                      AND (
                        direction_name ILIKE '%Программная инженерия%'
                        OR COALESCE(profile, '') ILIKE '%Программная инженерия%'
                        OR COALESCE(code, '') = '09.03.04'
                      )
                      AND study_form = 'part_time'
                      AND admission_type = 'paid'
                  ) AS moscow_software_part_time_paid_count,
                  COUNT(*) FILTER (
                    WHERE (region ILIKE '%Москва%' OR city ILIKE '%Москва%')
                      AND (
                        direction_name ILIKE '%Программная инженерия%'
                        OR COALESCE(profile, '') ILIKE '%Программная инженерия%'
                        OR COALESCE(code, '') = '09.03.04'
                      )
                      AND study_form = 'part_time'
                      AND admission_type = 'paid'
                      AND min_score <= $1
                  ) AS moscow_software_part_time_paid_score_count
                FROM backend_rows
                """,
                276 + AMBITIOUS_SCORE_MARGIN,
            )
            moscow_software_sample_rows = await connection.fetch(
                """
                SELECT
                  u.name AS university_name,
                  u.city,
                  u.region,
                  d.code,
                  d.name AS direction_name,
                  d.profile,
                  d.study_form::TEXT AS study_form,
                  ps.admission_type::TEXT AS admission_type,
                  ps.min_score,
                  ps.year
                FROM passing_scores ps
                JOIN directions d ON d.id = ps.direction_id
                JOIN universities u ON u.id = d.university_id
                LEFT JOIN faculties f ON f.id = d.faculty_id
                WHERE (u.region ILIKE '%Москва%' OR u.city ILIKE '%Москва%')
                  AND (
                    d.name ILIKE '%Программная инженерия%'
                    OR COALESCE(d.profile, '') ILIKE '%Программная инженерия%'
                    OR COALESCE(d.code, '') = '09.03.04'
                  )
                  AND NOT (
                    u.name ILIKE '%Региональный центр технологий и инженерии%'
                    OR u.name ILIKE '%Институт социальных и цифровых профессий%'
                    OR COALESCE(u.short_name, '') ~* '^(РЦТИ|ИСЦП)-[0-9]+$'
                  )
                ORDER BY ps.year DESC NULLS LAST, ps.min_score DESC NULLS LAST
                LIMIT 10
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
        moscow_api_default = await fetch_universities_postgres(
            pool,
            build_university_filters(
                {
                    "region": "Москва",
                    "city": "Москва",
                    "direction": "09.03.04 Программная инженерия",
                    "study_form": "заочная",
                    "type": "paid",
                    "score": "276",
                }
            ),
        )
        moscow_api_limit20 = await fetch_universities_postgres(
            pool,
            build_university_filters(
                {
                    "region": "Москва",
                    "city": "Москва",
                    "direction": "09.03.04 Программная инженерия",
                    "study_form": "заочная",
                    "type": "paid",
                    "score": "276",
                    "limit": "20",
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
    print(f"Direction code terms for 09.03.04 Программная инженерия: {direction_code_terms('09.03.04 Программная инженерия')}")
    print(f"Moscow all backend score rows: {moscow_diagnostics['moscow_all_count']}")
    print(f"Moscow software engineering rows: {moscow_diagnostics['moscow_software_count']}")
    print(f"Moscow software engineering part-time rows: {moscow_diagnostics['moscow_software_part_time_count']}")
    print(
        "Moscow software engineering part-time paid rows: "
        f"{moscow_diagnostics['moscow_software_part_time_paid_count']}"
    )
    print(
        f"Moscow software engineering part-time paid rows for score 276 (+{AMBITIOUS_SCORE_MARGIN} margin): "
        f"{moscow_diagnostics['moscow_software_part_time_paid_score_count']}"
    )
    print(f"Moscow API default rows: {len(moscow_api_default)}")
    print(f"Moscow API limit=20 rows: {len(moscow_api_limit20)}")
    print("Moscow software sample:")
    for row in moscow_software_sample_rows[:5]:
        print(
            "  - "
            f"{row['university_name']} | {row['code'] or ''} {row['direction_name'] or ''} | "
            f"{row['study_form'] or ''} | {row['admission_type'] or ''} | "
            f"{row['min_score']} | {row['year']}"
        )
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
