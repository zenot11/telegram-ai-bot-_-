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


DEFAULT_LIMIT = 5
MAX_LIMIT = 200

STUDY_FORM_LABELS = {
    "full_time": "очная",
    "part_time": "заочная",
    "evening": "очно-заочная",
}

POSTGRES_STUDY_FORMS = {
    "очная": "full_time",
    "очно": "full_time",
    "full_time": "full_time",
    "заочная": "part_time",
    "заочно": "part_time",
    "part_time": "part_time",
    "очно-заочная": "evening",
    "очнозаочная": "evening",
    "вечерняя": "evening",
    "evening": "evening",
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
    "бюджет": ["budget", "target", "special_quota", "separate_quota", "additional"],
    "платное": ["paid"],
}

SORT_OPTIONS = {
    "min_score_asc",
    "min_score_desc",
    "university",
    "city",
    "direction",
    "year_desc",
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


def parse_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    text = str(value).strip()
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


def normalize_limit(value: Any, default: int = DEFAULT_LIMIT, max_limit: int = MAX_LIMIT) -> int:
    parsed = parse_int(value, default)
    if parsed is None:
        parsed = default
    return max(1, min(parsed, max_limit))


clamp_limit = normalize_limit


def build_university_filters(params: Mapping[str, Any]) -> dict[str, Any]:
    sort = str(params.get("sort", "") or "").strip()
    return {
        "region": str(params.get("region", "") or "").strip(),
        "city": str(params.get("city", "") or "").strip(),
        "direction": str(params.get("direction", "") or "").strip(),
        "type": str(params.get("type", "") or "").strip(),
        "study_form": str(params.get("study_form", "") or "").strip(),
        "q": str(params.get("q", "") or "").strip(),
        "score": parse_int(params.get("score"), None),
        "year": parse_int(params.get("year"), None),
        "limit": normalize_limit(params.get("limit", DEFAULT_LIMIT)),
        "sort": sort if sort in SORT_OPTIONS else "",
    }


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
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, Any]]:
    filters = build_university_filters(
        {
            "region": region,
            "score": score,
            "direction": direction,
            "type": education_type,
            "limit": limit,
        }
    )
    return fetch_universities_json(rows, filters)


def fetch_universities_json(rows: list[dict[str, Any]], filters: Mapping[str, Any]) -> list[dict[str, Any]]:
    results = [item for item in rows if _json_record_matches(item, filters)]
    results = _sort_json_universities(results, str(filters.get("sort", "")))
    return results[: normalize_limit(filters.get("limit", DEFAULT_LIMIT))]


async def fetch_universities_postgres(pool: Any, filters: Mapping[str, Any]) -> list[dict[str, Any]]:
    query, params = _build_postgres_universities_query(filters)
    rows = await pool.fetch(query, *params)
    return [normalize_pg_record(row) for row in rows]


async def fetch_postgres_universities(
    pool: Any,
    region: str,
    score: int,
    direction: str,
    education_type: str,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, Any]]:
    filters = build_university_filters(
        {
            "region": region,
            "score": score,
            "direction": direction,
            "type": education_type,
            "limit": limit,
        }
    )
    return await fetch_universities_postgres(pool, filters)


async def count_postgres_universities(pool: Any) -> int:
    value = await pool.fetchval("SELECT COUNT(*) FROM universities")
    return int(value or 0)


def count_json_universities(records: list[dict[str, Any]]) -> int:
    return len(records)


def fetch_regions_json(records: list[dict[str, Any]]) -> list[str]:
    return _sorted_unique(item.get("region") for item in records)


async def fetch_regions_postgres(pool: Any) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT DISTINCT region
        FROM universities
        WHERE region IS NOT NULL AND btrim(region) <> ''
        ORDER BY region
        """
    )
    return _sorted_unique(row["region"] for row in rows)


def fetch_cities_json(records: list[dict[str, Any]], region: str = "") -> list[str]:
    return _sorted_unique(
        item.get("city")
        for item in records
        if not region or _region_matches(item.get("region", ""), region)
    )


async def fetch_cities_postgres(pool: Any, region: str = "") -> list[str]:
    params: list[Any] = []
    where_parts = ["city IS NOT NULL", "btrim(city) <> ''"]
    if region:
        params.append(f"%{normalize_region(region)}%")
        where_parts.append(f"region ILIKE ${len(params)}")
    rows = await pool.fetch(
        f"""
        SELECT DISTINCT city
        FROM universities
        WHERE {" AND ".join(where_parts)}
        ORDER BY city
        """,
        *params,
    )
    return _sorted_unique(row["city"] for row in rows)


def fetch_directions_json(records: list[dict[str, Any]], filters: Mapping[str, Any]) -> list[str]:
    values = []
    for item in records:
        if _json_record_matches(item, {**filters, "score": None, "direction": ""}):
            values.extend([item.get("direction"), item.get("program")])
    return _sorted_unique(values)


async def fetch_directions_postgres(pool: Any, filters: Mapping[str, Any]) -> list[str]:
    where_sql, params = _build_postgres_directory_where(filters, include_direction=False)
    rows = await pool.fetch(
        f"""
        SELECT DISTINCT d.name AS direction
        FROM directions d
        JOIN universities u ON u.id = d.university_id
        LEFT JOIN passing_scores ps ON ps.direction_id = d.id
        LEFT JOIN faculties f ON f.id = d.faculty_id
        WHERE {where_sql}
        ORDER BY d.name
        """,
        *params,
    )
    return _sorted_unique(row["direction"] for row in rows)


def fetch_study_forms_json(records: list[dict[str, Any]]) -> list[str]:
    return _sorted_unique(normalize_study_form(item.get("study_form")) for item in records)


async def fetch_study_forms_postgres(pool: Any) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT DISTINCT study_form::TEXT AS study_form
        FROM directions
        WHERE study_form IS NOT NULL
        ORDER BY study_form::TEXT
        """
    )
    return _sorted_unique(normalize_study_form(row["study_form"]) for row in rows)


def fetch_admission_types_json(records: list[dict[str, Any]]) -> list[str]:
    return _sorted_unique(normalize_type(item.get("type")) for item in records)


async def fetch_admission_types_postgres(pool: Any) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT DISTINCT admission_type::TEXT AS admission_type
        FROM passing_scores
        WHERE admission_type IS NOT NULL
        ORDER BY admission_type::TEXT
        """
    )
    return _sorted_unique(normalize_type(row["admission_type"]) for row in rows)


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
    admission_type = _string_value(_row_value(row, "admission_type", _row_value(row, "type", "")))
    row_type = normalize_type(admission_type) or "бюджет"

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
        "year": _row_value(row, "year", _row_value(row, "latest_year", None)),
        "faculty": _string_value(_row_value(row, "faculty", _row_value(row, "faculty_name", ""))),
        "admission_type": admission_type,
        "university_short_name": _string_value(_row_value(row, "university_short_name", "")),
        "source": _string_value(_row_value(row, "source", "postgresql")),
    }


def normalize_study_form(value: Any) -> str:
    normalized = normalize(value)
    if not normalized:
        return ""
    return STUDY_FORM_LABELS.get(normalized, str(value).strip())


def postgres_study_form(value: Any) -> str | None:
    return POSTGRES_STUDY_FORMS.get(normalize(value))


def postgres_admission_types(value: Any) -> list[str]:
    return POSTGRES_ADMISSION_BY_API_TYPE.get(normalize_type(value), [])


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


def _json_record_matches(item: dict[str, Any], filters: Mapping[str, Any]) -> bool:
    if filters.get("region") and not _region_matches(item.get("region", ""), str(filters["region"])):
        return False
    if filters.get("city") and not _text_matches(item.get("city", ""), str(filters["city"])):
        return False

    score = filters.get("score")
    if score is not None:
        min_score = _min_score(item)
        if min_score is None or min_score > int(score) + AMBITIOUS_SCORE_MARGIN:
            return False

    requested_type = normalize_type(filters.get("type", ""))
    if requested_type and normalize_type(item.get("type", "")) != requested_type:
        return False

    requested_study_form = normalize_study_form(filters.get("study_form", ""))
    if requested_study_form:
        item_study_form = normalize_study_form(item.get("study_form", ""))
        if not item_study_form or normalize(item_study_form) != normalize(requested_study_form):
            return False

    year = filters.get("year")
    item_year = parse_int(item.get("year", item.get("latest_year")), None)
    if year is not None and item_year is not None and item_year != year:
        return False

    direction = str(filters.get("direction", "") or "")
    if direction and not direction_matches(item, direction):
        return False

    q = str(filters.get("q", "") or "")
    if q and not _json_q_matches(item, q):
        return False

    return True


def _build_postgres_universities_query(filters: Mapping[str, Any]) -> tuple[str, list[Any]]:
    params: list[Any] = []
    score_where = ["min_score IS NOT NULL"]
    where_parts = ["ps.min_score IS NOT NULL"]

    def add_param(value: Any) -> str:
        params.append(value)
        return f"${len(params)}"

    year = filters.get("year")
    if year is not None:
        year_param = add_param(year)
        score_where.append(f"year = {year_param}")

    _append_postgres_common_filters(where_parts, params, filters)

    score = filters.get("score")
    if score is not None:
        max_score = add_param(int(score) + AMBITIOUS_SCORE_MARGIN)
        where_parts.append(f"ps.min_score <= {max_score}")

    order_sql = _postgres_order_by(str(filters.get("sort", "")), score is not None)
    limit_param = add_param(normalize_limit(filters.get("limit", DEFAULT_LIMIT)))
    where_sql = " AND ".join(where_parts)
    score_where_sql = " AND ".join(score_where)

    query = f"""
        WITH latest_scores AS (
            SELECT DISTINCT ON (direction_id, admission_type)
                direction_id,
                year,
                admission_type,
                min_score,
                note
            FROM passing_scores
            WHERE {score_where_sql}
            ORDER BY direction_id, admission_type, year DESC
        )
        SELECT
            COALESCE(NULLIF(u.short_name, ''), u.name) AS university,
            u.name AS university_name,
            u.short_name AS university_short_name,
            u.city,
            u.region,
            u.website AS url,
            d.name AS program,
            d.name AS direction,
            d.profile,
            d.study_form::TEXT AS study_form,
            f.name AS faculty,
            ps.year,
            ps.admission_type::TEXT AS admission_type,
            ps.min_score,
            ps.note,
            'postgresql' AS source
        FROM latest_scores ps
        JOIN directions d ON d.id = ps.direction_id
        JOIN universities u ON u.id = d.university_id
        LEFT JOIN faculties f ON f.id = d.faculty_id
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT {limit_param}
    """
    return query, params


def _build_postgres_directory_where(
    filters: Mapping[str, Any],
    include_direction: bool = True,
) -> tuple[str, list[Any]]:
    params: list[Any] = []
    where_parts = ["d.name IS NOT NULL", "btrim(d.name) <> ''"]

    year = filters.get("year")
    if year is not None:
        params.append(year)
        where_parts.append(f"ps.year = ${len(params)}")

    _append_postgres_common_filters(where_parts, params, filters, include_direction=include_direction)
    return " AND ".join(where_parts), params


def _append_postgres_common_filters(
    where_parts: list[str],
    params: list[Any],
    filters: Mapping[str, Any],
    include_direction: bool = True,
) -> None:
    def add_param(value: Any) -> str:
        params.append(value)
        return f"${len(params)}"

    if filters.get("region"):
        region_pattern = add_param(f"%{normalize_region(str(filters['region']))}%")
        where_parts.append(f"u.region ILIKE {region_pattern}")

    if filters.get("city"):
        city_pattern = add_param(f"%{filters['city']}%")
        where_parts.append(f"u.city ILIKE {city_pattern}")

    admission_types = postgres_admission_types(filters.get("type", ""))
    if admission_types:
        admission_param = add_param(admission_types)
        where_parts.append(f"ps.admission_type::TEXT = ANY({admission_param}::TEXT[])")
    elif normalize(filters.get("type", "")):
        where_parts.append("FALSE")

    study_form = postgres_study_form(filters.get("study_form", ""))
    if study_form:
        study_form_param = add_param(study_form)
        where_parts.append(f"d.study_form::TEXT = {study_form_param}")
    elif normalize(filters.get("study_form", "")):
        where_parts.append("FALSE")

    if include_direction:
        direction_terms = postgres_direction_terms(str(filters.get("direction", "") or ""))
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

    q = str(filters.get("q", "") or "").strip()
    if q:
        q_param = add_param(f"%{q}%")
        where_parts.append(
            "("
            f"u.name ILIKE {q_param} "
            f"OR COALESCE(u.short_name, '') ILIKE {q_param} "
            f"OR COALESCE(u.city, '') ILIKE {q_param} "
            f"OR COALESCE(u.region, '') ILIKE {q_param} "
            f"OR d.name ILIKE {q_param} "
            f"OR COALESCE(d.profile, '') ILIKE {q_param} "
            f"OR COALESCE(f.name, '') ILIKE {q_param}"
            ")"
        )


def _postgres_order_by(sort: str, has_score: bool) -> str:
    if sort == "min_score_desc":
        return "ps.min_score DESC NULLS LAST, u.name ASC, d.name ASC"
    if sort == "university":
        return "u.name ASC, d.name ASC, ps.min_score ASC NULLS LAST"
    if sort == "city":
        return "u.city ASC NULLS LAST, u.name ASC, d.name ASC"
    if sort == "direction":
        return "d.name ASC, u.name ASC, ps.min_score ASC NULLS LAST"
    if sort == "year_desc":
        return "ps.year DESC NULLS LAST, u.name ASC, d.name ASC"
    if sort == "min_score_asc" or has_score:
        return "ps.min_score ASC NULLS LAST, u.name ASC, d.name ASC"
    return "u.name ASC, d.name ASC, ps.min_score ASC NULLS LAST"


def _sort_json_universities(rows: list[dict[str, Any]], sort: str) -> list[dict[str, Any]]:
    if sort == "min_score_asc":
        return sorted(rows, key=lambda item: (_min_score(item) is None, _min_score(item) or 0))
    if sort == "min_score_desc":
        return sorted(rows, key=lambda item: (_min_score(item) is None, -(_min_score(item) or 0)))
    if sort == "university":
        return sorted(rows, key=lambda item: normalize(item.get("university", "")))
    if sort == "city":
        return sorted(rows, key=lambda item: (normalize(item.get("city", "")), normalize(item.get("university", ""))))
    if sort == "direction":
        return sorted(rows, key=lambda item: (normalize(item.get("direction", "")), normalize(item.get("program", ""))))
    if sort == "year_desc":
        return sorted(rows, key=lambda item: -(parse_int(item.get("year", item.get("latest_year")), 0) or 0))
    return rows


def _json_q_matches(item: dict[str, Any], query: str) -> bool:
    values = [
        item.get("university", ""),
        item.get("city", ""),
        item.get("region", ""),
        item.get("program", ""),
        item.get("direction", ""),
        item.get("study_form", ""),
        item.get("note", ""),
        " ".join(item.get("directions") or []),
    ]
    return _text_matches(" ".join(str(value) for value in values if value), query)


def _region_matches(value: Any, requested: str) -> bool:
    requested_region = normalize_region(requested)
    item_region = normalize_region(str(value or ""))
    return item_region == requested_region or _text_matches(item_region, requested_region)


def _text_matches(value: Any, requested: str) -> bool:
    normalized_value = normalize(value)
    normalized_requested = normalize(requested)
    return bool(normalized_requested) and normalized_requested in normalized_value


def _sorted_unique(values: Any) -> list[str]:
    items = {_string_value(value) for value in values if _string_value(value)}
    return sorted(items, key=normalize)


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
