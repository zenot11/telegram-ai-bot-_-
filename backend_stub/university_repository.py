from collections.abc import Mapping
from typing import Any

from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN
from telegram_bot.services.validation import (
    DIRECTION_SYNONYMS,
    education_type_label,
    normalize_direction,
    normalize_education_type,
    normalize_region,
    normalize_text,
)


STUDY_FORM_LABELS = {
    "full_time": "очная",
    "part_time": "заочная",
    "evening": "очно-заочная",
}

BUDGET_ADMISSION_TYPES = {
    "budget",
    "target",
    "special_quota",
    "separate_quota",
    "additional",
    "бюджет",
    "целевая",
    "целевая квота",
    "особая квота",
    "отдельная квота",
}

PAID_ADMISSION_TYPES = {
    "paid",
    "платное",
    "платно",
    "контракт",
    "договор",
}

POSTGRES_ADMISSION_BY_API_TYPE = {
    "бюджет": "budget",
    "платное": "paid",
}


def normalize(text: Any) -> str:
    if text is None:
        return ""
    return normalize_text(str(text))


def normalize_type(value: Any) -> str:
    normalized = normalize(value)
    if normalized in BUDGET_ADMISSION_TYPES:
        return "бюджет"
    if normalized in PAID_ADMISSION_TYPES:
        return "платное"

    education_type = normalize_education_type(str(value or ""))
    if education_type:
        return education_type_label(education_type)
    return normalized


def direction_matches(item: dict[str, Any], direction: str) -> bool:
    requested = normalize_direction(direction)
    if not requested:
        return True

    values = [
        item.get("program", ""),
        item.get("direction", ""),
        " ".join(item.get("directions") or []),
    ]
    haystack = " ".join(values)
    requested_direction = normalize_direction(requested)
    item_direction = normalize_direction(haystack)
    if normalize(requested_direction) == normalize(item_direction):
        return True

    normalized_requested = normalize(requested)
    normalized_haystack = normalize(haystack)
    return normalized_requested in normalized_haystack or any(
        part and part in normalized_haystack for part in normalized_requested.split()
    )


def filter_json_universities(
    rows: list[dict[str, Any]],
    region: str,
    score: int,
    direction: str,
    education_type: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    normalized_region = normalize_region(region)
    normalized_type = normalize_type(education_type)
    safe_limit = normalize_limit(limit)

    results = []
    for item in rows:
        if normalized_region and normalize_region(item.get("region", "")) != normalized_region:
            continue

        min_score = _min_score(item)
        if min_score is None or min_score > score + AMBITIOUS_SCORE_MARGIN:
            continue

        if normalized_type and normalize_type(item.get("type", "")) != normalized_type:
            continue

        if not direction_matches(item, direction):
            continue

        results.append(item)

    return results[:safe_limit]


async def fetch_postgres_universities(
    pool: Any,
    region: str,
    score: int,
    direction: str,
    education_type: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    safe_limit = normalize_limit(limit)
    where_parts = ["ps.min_score IS NOT NULL"]
    params: list[Any] = []

    def add_param(value: Any) -> str:
        params.append(value)
        return f"${len(params)}"

    normalized_region = normalize_region(region)
    if normalized_region:
        region_pattern = add_param(f"%{normalized_region}%")
        where_parts.append(f"(u.region ILIKE {region_pattern} OR u.city ILIKE {region_pattern})")

    max_score = add_param(score + AMBITIOUS_SCORE_MARGIN)
    where_parts.append(f"ps.min_score <= {max_score}")

    admission_type = postgres_admission_type(education_type)
    if admission_type:
        admission_param = add_param(admission_type)
        where_parts.append(f"ps.admission_type = {admission_param}::admission_type_enum")
    elif normalize(education_type):
        where_parts.append("FALSE")

    direction_terms = postgres_direction_terms(direction)
    if direction_terms:
        direction_conditions = []
        for term in direction_terms:
            term_param = add_param(f"%{term}%")
            direction_conditions.append(
                "("
                f"d.name ILIKE {term_param} "
                f"OR COALESCE(d.profile, '') ILIKE {term_param} "
                f"OR COALESCE(f.name, '') ILIKE {term_param}"
                ")"
            )
        where_parts.append("(" + " OR ".join(direction_conditions) + ")")

    limit_param = add_param(safe_limit)
    where_sql = " AND ".join(where_parts)
    query = f"""
        WITH latest_scores AS (
            SELECT DISTINCT ON (direction_id, admission_type)
                direction_id,
                year,
                admission_type,
                min_score,
                note
            FROM passing_scores
            WHERE min_score IS NOT NULL
            ORDER BY direction_id, admission_type, year DESC
        )
        SELECT
            COALESCE(NULLIF(u.short_name, ''), u.name) AS university,
            u.name AS university_name,
            u.city,
            u.region,
            u.website AS url,
            d.name AS program,
            d.name AS direction,
            d.profile,
            d.study_form::TEXT AS study_form,
            ps.admission_type::TEXT AS type,
            ps.min_score,
            ps.note
        FROM latest_scores ps
        JOIN directions d ON d.id = ps.direction_id
        JOIN universities u ON u.id = d.university_id
        LEFT JOIN faculties f ON f.id = d.faculty_id
        WHERE {where_sql}
        ORDER BY ps.min_score ASC, u.name ASC, d.name ASC
        LIMIT {limit_param}
    """
    rows = await pool.fetch(query, *params)
    return [normalize_pg_record(row) for row in rows]


async def count_postgres_universities(pool: Any) -> int:
    value = await pool.fetchval("SELECT COUNT(*) FROM universities")
    return int(value or 0)


def count_json_universities(records: list[dict[str, Any]]) -> int:
    return len(records)


def normalize_pg_record(row: Any) -> dict[str, Any]:
    subjects = _row_value(row, "subjects", [])
    if isinstance(subjects, str):
        subjects_value = [part.strip() for part in subjects.split(",") if part.strip()]
    elif isinstance(subjects, list):
        subjects_value = [str(subject).strip() for subject in subjects if str(subject).strip()]
    else:
        subjects_value = []

    min_score = _int_value(_row_value(row, "min_score", _row_value(row, "passing_score", 0)))
    study_form = normalize_study_form(_row_value(row, "study_form", ""))
    row_type = normalize_type(_row_value(row, "type", _row_value(row, "admission_type", ""))) or "бюджет"

    return {
        "university": _string_value(_row_value(row, "university", _row_value(row, "university_name", ""))),
        "city": _string_value(_row_value(row, "city", "")),
        "region": _string_value(_row_value(row, "region", "")),
        "program": _string_value(_row_value(row, "program", _row_value(row, "direction_name", ""))),
        "direction": _string_value(_row_value(row, "direction", _row_value(row, "direction_name", ""))),
        "subjects": subjects_value,
        "min_score": min_score,
        "type": row_type,
        "url": _string_value(_row_value(row, "url", _row_value(row, "website", ""))),
        "price": _row_value(row, "price", None),
        "study_form": study_form,
        "duration": _string_value(_row_value(row, "duration", "")),
        "note": _string_value(_row_value(row, "note", "")),
    }


def normalize_study_form(value: Any) -> str:
    normalized = normalize(value)
    if not normalized:
        return ""
    return STUDY_FORM_LABELS.get(normalized, str(value).strip())


def postgres_admission_type(value: str) -> str | None:
    return POSTGRES_ADMISSION_BY_API_TYPE.get(normalize_type(value))


def postgres_direction_terms(value: str) -> list[str]:
    requested = normalize_direction(value)
    if not requested:
        return []

    terms = {requested, value}
    for direction, synonyms in DIRECTION_SYNONYMS.items():
        if normalize_direction(requested) == direction or normalize(requested) == normalize(direction):
            terms.add(direction)
            terms.update(synonyms)

    result = []
    for term in terms:
        cleaned = " ".join(str(term).strip().split())
        if cleaned and cleaned not in result:
            result.append(cleaned)
    return result[:12]


def normalize_limit(limit: int) -> int:
    return max(1, min(limit, 20))


def _min_score(item: dict[str, Any]) -> int | None:
    value = item.get("min_score")
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _row_value(row: Any, key: str, default: Any = None) -> Any:
    if isinstance(row, Mapping):
        return row.get(key, default)
    try:
        return row[key]
    except (KeyError, TypeError, IndexError):
        return default


def _string_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _int_value(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return 0
