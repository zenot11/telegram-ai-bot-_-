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
    direction_search_terms,
    fetch_achievements_postgres,
    fetch_directions_postgres,
    fetch_regions_postgres,
    fetch_universities_postgres,
    postgres_admission_type_values,
    postgres_admission_types,
    postgres_study_form,
    region_search_terms,
)
from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN  # noqa: E402
from telegram_bot.services.scores import MIN_REASONABLE_SCORE  # noqa: E402


REQUIRED_TABLES = ("universities", "directions", "passing_scores", "achievements")
SYNTHETIC_SQL = (
    "u.name ILIKE '%Региональный центр технологий и инженерии%' "
    "OR u.name ILIKE '%Институт социальных и цифровых профессий%' "
    "OR COALESCE(u.short_name, '') ~* '^(РЦТИ|ИСЦП)-[0-9]+$'"
)

COVERAGE_AUDIT_SCENARIOS = [
    {"label": "IT / Москва / budget / full_time", "direction": "IT", "region": "Москва", "type": "budget", "study_form": "очная"},
    {"label": "IT / Крым / budget", "direction": "IT", "region": "Республика Крым", "type": "budget"},
    {"label": "медицина / Татарстан / budget", "direction": "медицина", "region": "Татарстан", "type": "budget"},
    {"label": "экономика / Москва / paid", "direction": "экономика", "region": "Москва", "type": "paid"},
    {"label": "педагогика / Адыгея / budget", "direction": "педагогика", "region": "Республика Адыгея", "type": "budget"},
    {"label": "юриспруденция / Санкт-Петербург / budget", "direction": "юриспруденция", "region": "Санкт-Петербург", "type": "budget"},
    {"label": "строительство/архитектура / Краснодарский край", "direction": "строительство", "region": "Краснодарский край"},
    {"label": "экология/география / Ростовская область", "direction": "экология", "region": "Ростовская область"},
    {"label": "01.03.02 ПМИ / Москва / budget", "direction": "01.03.02 ПМИ", "region": "Москва", "type": "budget"},
    {"label": "09.03.04 Программная инженерия / Москва / paid / part_time", "direction": "09.03.04 Программная инженерия", "region": "Москва", "type": "paid", "study_form": "заочная"},
    {"label": "paid / очно-заочная", "type": "paid", "study_form": "очно-заочная"},
    {"label": "target quota / budget", "admission_type": "целевая квота", "type": "budget"},
    {"label": "special quota / budget", "admission_type": "особая квота", "type": "budget"},
]


async def fetch_coverage_audit_scenario(connection: Any, scenario: dict[str, str]) -> dict[str, Any]:
    where_parts: list[str] = ["ps.min_score IS NOT NULL"]
    params: list[Any] = []
    match_mode = "all"

    def add_param(value: Any) -> str:
        params.append(value)
        return f"${len(params)}"

    region = scenario.get("region", "")
    if region:
        region_conditions = []
        for term in region_search_terms(region):
            region_conditions.append(f"u.region ILIKE {add_param(f'%{term}%')} OR u.city ILIKE {add_param(f'%{term}%')}")
        where_parts.append("(" + " OR ".join(region_conditions) + ")")

    direction = scenario.get("direction", "")
    if direction:
        code_terms = direction_code_terms(direction)
        direction_conditions = []
        if code_terms:
            direction_conditions.append(f"COALESCE(d.code, '') = ANY({add_param(code_terms)}::TEXT[])")
            match_mode = "exact_code"
        else:
            direction_terms = direction_search_terms(direction)
            if direction_terms:
                match_mode = "alias_or_text"
            for term in direction_terms[:16]:
                pattern = add_param(f"%{term}%")
                direction_conditions.append(
                    "("
                    f"d.name ILIKE {pattern} "
                    f"OR COALESCE(d.profile, '') ILIKE {pattern}"
                    ")"
                )
        if direction_conditions:
            where_parts.append("(" + " OR ".join(direction_conditions) + ")")

    admission_types = postgres_admission_types(scenario.get("type", ""))
    if admission_types:
        where_parts.append(f"ps.admission_type::TEXT = ANY({add_param(admission_types)}::TEXT[])")

    exact_admission_types = postgres_admission_type_values(scenario.get("admission_type", ""))
    if exact_admission_types:
        where_parts.append(f"ps.admission_type::TEXT = ANY({add_param(exact_admission_types)}::TEXT[])")

    study_form = postgres_study_form(scenario.get("study_form", ""))
    if study_form:
        where_parts.append(f"d.study_form::TEXT = {add_param(study_form)}")

    where_sql = " AND ".join(where_parts)
    count_row = await connection.fetchrow(
        f"""
        SELECT
          COUNT(*) AS total_count,
          COUNT(*) FILTER (WHERE NOT ({SYNTHETIC_SQL})) AS regular_count,
          COUNT(*) FILTER (WHERE NOT ({SYNTHETIC_SQL}) AND ps.min_score >= {MIN_REASONABLE_SCORE}) AS valid_count,
          COUNT(*) FILTER (WHERE NOT ({SYNTHETIC_SQL}) AND ps.min_score > 1 AND ps.min_score < {MIN_REASONABLE_SCORE}) AS suspicious_count
        FROM passing_scores ps
        JOIN directions d ON d.id = ps.direction_id
        JOIN universities u ON u.id = d.university_id
        LEFT JOIN faculties f ON f.id = d.faculty_id
        WHERE {where_sql}
        """,
        *params,
    )
    sample_rows = await connection.fetch(
        f"""
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
        WHERE {where_sql}
          AND NOT ({SYNTHETIC_SQL})
        ORDER BY
          (ps.min_score >= {MIN_REASONABLE_SCORE}) DESC,
          ps.year DESC NULLS LAST,
          ps.min_score DESC NULLS LAST,
          u.name ASC
        LIMIT 3
        """,
        *params,
    )
    return {
        "label": scenario["label"],
        "match_mode": match_mode,
        "total_count": int(count_row["total_count"] or 0),
        "regular_count": int(count_row["regular_count"] or 0),
        "valid_count": int(count_row["valid_count"] or 0),
        "suspicious_count": int(count_row["suspicious_count"] or 0),
        "sample_rows": sample_rows,
    }


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
            coverage_audit_rows = [
                await fetch_coverage_audit_scenario(connection, scenario)
                for scenario in COVERAGE_AUDIT_SCENARIOS
            ]

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
    except Exception as exc:
        print("PostgreSQL check failed: connection or query failed. Check DATABASE_URL, schema and seed data.")
        print(f"Error detail: {type(exc).__name__}: {exc}")
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
    print("Coverage audit:")
    for audit in coverage_audit_rows:
        print(
            "  - "
            f"{audit['label']}: total={audit['total_count']}, "
            f"regular={audit['regular_count']}, valid={audit['valid_count']}, "
            f"suspicious={audit['suspicious_count']}, match={audit['match_mode']}"
        )
        for sample_row in audit["sample_rows"]:
            print(
                "      "
                f"{sample_row['university_name']} | {sample_row['code'] or ''} "
                f"{sample_row['direction_name'] or ''} | "
                f"{sample_row['study_form'] or ''} | {sample_row['admission_type'] or ''} | "
                f"{sample_row['min_score']} | {sample_row['year']}"
            )
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
