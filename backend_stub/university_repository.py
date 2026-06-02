from collections.abc import Mapping
import re
from typing import Any

from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN
from telegram_bot.services.scores import (
    MIN_REASONABLE_SCORE,
    is_suspicious_score,
    is_valid_score,
    score_display,
    score_note,
)
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
ACHIEVEMENTS_DEFAULT_LIMIT = 20
DIRECTION_CODE_RE = re.compile(r"\b\d{2}\.\d{2}\.\d{2}\b")

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
    "target_quota",
    "special",
    "special_quota",
    "separate",
    "separate_quota",
    "individual_quota",
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

ADMISSION_TYPE_LABELS = {
    "budget": "бюджет",
    "paid": "платное",
    "target": "целевая квота",
    "target_quota": "целевая квота",
    "special": "особая квота",
    "special_quota": "особая квота",
    "separate": "отдельная квота",
    "separate_quota": "отдельная квота",
    "individual_quota": "отдельная квота",
    "additional": "дополнительный набор",
}

CONTEST_LABELS = {
    "budget": "общий конкурс",
    "бюджет": "общий конкурс",
    "общий_бюджет": "общий конкурс",
    "общий_конкурс": "общий конкурс",
    "paid": "",
    "платное": "",
    "target": "целевая квота",
    "target_quota": "целевая квота",
    "целевая": "целевая квота",
    "целевая_квота": "целевая квота",
    "special": "особая квота",
    "special_quota": "особая квота",
    "особая_квота": "особая квота",
    "separate": "отдельная квота",
    "separate_quota": "отдельная квота",
    "individual_quota": "отдельная квота",
    "отдельная_квота": "отдельная квота",
    "additional": "дополнительный набор",
    "дополнительный_набор": "дополнительный набор",
}

POSTGRES_ADMISSION_BY_LABEL = {
    "бюджет": ["budget"],
    "общий бюджет": ["budget"],
    "budget": ["budget"],
    "платное": ["paid"],
    "paid": ["paid"],
    "контракт": ["paid"],
    "целевая": ["target"],
    "целевая квота": ["target"],
    "target": ["target"],
    "target_quota": ["target"],
    "особая квота": ["special_quota"],
    "special": ["special_quota"],
    "special_quota": ["special_quota"],
    "отдельная квота": ["separate_quota"],
    "separate": ["separate_quota"],
    "separate_quota": ["separate_quota"],
    "individual_quota": ["separate_quota"],
    "дополнительный набор": ["additional"],
    "дополнительный прием": ["additional"],
    "additional": ["additional"],
}

REGION_ALIAS_GROUPS = {
    "адыгея": ["Республика Адыгея", "Адыгея"],
    "республика адыгея": ["Республика Адыгея", "Адыгея"],
    "крым": ["Республика Крым", "Крым"],
    "республика крым": ["Республика Крым", "Крым"],
    "татарстан": ["Республика Татарстан", "Татарстан"],
    "республика татарстан": ["Республика Татарстан", "Татарстан"],
}

POSTGRES_DIRECTION_PRESETS = {
    "IT": (
        "Прикладная информатика",
        "Информационная безопасность",
        "Информационные системы и технологии",
        "Программная инженерия",
        "Информатика и вычислительная техника",
        "Бизнес-информатика",
        "Большие и открытые данные",
        "Математическое обеспечение и администрирование информационных систем",
    ),
    "медицина": (
        "Лечебное дело",
        "Педиатрия",
        "Стоматология",
        "Фармация",
        "Медико-профилактическое дело",
    ),
    "экономика": (
        "Экономика",
        "Экономическая безопасность",
        "Менеджмент",
        "Бизнес-информатика",
        "Государственное и муниципальное управление",
    ),
    "юриспруденция": (
        "Юриспруденция",
        "Правовое обеспечение национальной безопасности",
    ),
    "педагогика": (
        "Педагогическое образование",
        "Психолого-педагогическое образование",
        "Специальное дефектологическое образование",
    ),
    "строительство": (
        "Архитектура",
        "Строительство",
        "Градостроительство",
    ),
    "экология": (
        "Экология и природопользование",
        "География",
        "Картография и геоинформатика",
    ),
}

ACHIEVEMENTS_FALLBACK = [
    {
        "title": "Золотая медаль за окончание школы",
        "category": "аттестат",
        "points": 5,
        "description": "Ориентировочный максимум. Точные баллы нужно проверять в правилах конкретного вуза.",
    },
    {
        "title": "Знак отличия ГТО",
        "category": "спорт",
        "points": 3,
        "description": "Баллы за ГТО зависят от правил приёма конкретного вуза.",
    },
    {
        "title": "Олимпиады школьников",
        "category": "олимпиады",
        "points": 10,
        "description": "Олимпиады могут давать баллы или особые права, если вуз учитывает конкретный диплом.",
    },
]

TECHNICAL_UNIVERSITY_RE = re.compile(r"^[A-ZА-ЯЁ]{2,}[-_]?\d+$", re.IGNORECASE)
SYNTHETIC_UNIVERSITY_SHORT_NAME_RE = re.compile(r"^(?:РЦТИ|ИСЦП)-\d+$", re.IGNORECASE)
SYNTHETIC_UNIVERSITY_NAME_MARKERS = (
    "региональный центр технологий и инженерии",
    "институт социальных и цифровых профессий",
)
KNOWN_UNIVERSITY_ABBREVIATIONS = {
    "МГУ",
    "СПБГУ",
    "МФТИ",
    "МИРЭА",
    "КФУ",
    "РУДН",
    "ВШЭ",
    "МАИ",
    "МЭИ",
    "МГТУ",
    "РЭУ",
    "МАДИ",
    "МТУСИ",
    "МИИТ",
    "РАНХИГС",
    "ФУ",
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


def parse_bool(value: Any) -> bool:
    return normalize(value) in {"1", "true", "yes", "on", "да"}


def normalize_limit(value: Any, default: int = DEFAULT_LIMIT, max_limit: int = MAX_LIMIT) -> int:
    parsed = parse_int(value, default)
    if parsed is None:
        parsed = default
    return max(1, min(parsed, max_limit))


clamp_limit = normalize_limit


def build_university_filters(params: Mapping[str, Any]) -> dict[str, Any]:
    sort = str(params.get("sort", "") or "").strip()
    include_synthetic = parse_bool(params.get("include_synthetic")) or parse_bool(params.get("include_demo"))
    return {
        "region": str(params.get("region", "") or "").strip(),
        "city": str(params.get("city", "") or "").strip(),
        "direction": str(params.get("direction", "") or "").strip(),
        "type": str(params.get("type", "") or "").strip(),
        "admission_type": str(params.get("admission_type", "") or "").strip(),
        "study_form": str(params.get("study_form", "") or "").strip(),
        "q": str(params.get("q", "") or "").strip(),
        "score": parse_int(params.get("score"), None),
        "year": parse_int(params.get("year"), None),
        "limit": normalize_limit(params.get("limit", DEFAULT_LIMIT)),
        "sort": sort if sort in SORT_OPTIONS else "",
        "include_synthetic": include_synthetic,
    }


def direction_matches(item: dict[str, Any], direction: str) -> bool:
    terms = direction_search_terms(direction)
    if not terms:
        return True

    values = [
        item.get("program", ""),
        item.get("direction", ""),
        item.get("profile", ""),
        " ".join(item.get("directions") or []),
    ]
    haystack = " ".join(values)
    normalized_haystack = normalize(haystack)
    return any(_term_matches_haystack(term, normalized_haystack) for term in terms)


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
    include_synthetic = bool(filters.get("include_synthetic"))
    results = [
        with_display_labels(item)
        for item in rows
        if _json_record_matches(item, filters) and (include_synthetic or not is_synthetic_university_record(item))
    ]
    results = _sort_json_universities(results, str(filters.get("sort", "")))
    return results[: normalize_limit(filters.get("limit", DEFAULT_LIMIT))]


async def fetch_universities_postgres(pool: Any, filters: Mapping[str, Any]) -> list[dict[str, Any]]:
    direction = str(filters.get("direction", "") or "")
    if direction_code_terms(direction):
        exact_filters = {**filters, "_direction_match_mode": "exact_code"}
        query, params = _build_postgres_universities_query(exact_filters)
        rows = await pool.fetch(query, *params)
        if not rows:
            fallback_filters = {**filters, "_direction_match_mode": "code_text_fallback"}
            query, params = _build_postgres_universities_query(fallback_filters)
            rows = await pool.fetch(query, *params)
    else:
        query, params = _build_postgres_universities_query(filters)
        rows = await pool.fetch(query, *params)
    records = [normalize_pg_record(row) for row in rows]
    if filters.get("include_synthetic"):
        return records
    return [record for record in records if not is_synthetic_university_record(record)]


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
    has_query = bool(str(filters.get("q", "") or "").strip())
    rows = await pool.fetch(
        f"""
        SELECT DISTINCT
          d.name AS direction,
          d.code,
          d.profile
        FROM directions d
        JOIN universities u ON u.id = d.university_id
        LEFT JOIN passing_scores ps ON ps.direction_id = d.id
        LEFT JOIN faculties f ON f.id = d.faculty_id
        WHERE {where_sql}
        ORDER BY d.name, d.code, d.profile
        """,
        *params,
    )
    if has_query:
        return _sorted_unique(format_direction_directory_item(row["direction"], row["code"], row["profile"]) for row in rows)
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
    return _sorted_unique(admission_type_label(row["admission_type"]) for row in rows)


def fetch_achievements_json(limit: int = ACHIEVEMENTS_DEFAULT_LIMIT) -> list[dict[str, Any]]:
    return ACHIEVEMENTS_FALLBACK[: normalize_limit(limit, ACHIEVEMENTS_DEFAULT_LIMIT)]


async def fetch_achievements_postgres(pool: Any, limit: int = ACHIEVEMENTS_DEFAULT_LIMIT) -> list[dict[str, Any]]:
    rows = await pool.fetch(
        """
        SELECT code, name, max_points, description
        FROM achievements
        ORDER BY max_points DESC, name ASC
        LIMIT $1
        """,
        normalize_limit(limit, ACHIEVEMENTS_DEFAULT_LIMIT),
    )
    return [normalize_achievement(row) for row in rows]


def normalize_achievement(row: Any) -> dict[str, Any]:
    code = _string_value(_row_value(row, "code", ""))
    return {
        "title": _string_value(_row_value(row, "title", _row_value(row, "name", ""))),
        "category": _string_value(_row_value(row, "category", achievement_category(code))),
        "points": _int_value(_row_value(row, "points", _row_value(row, "max_points", 0))),
        "description": _string_value(_row_value(row, "description", "")),
    }


def normalize_pg_record(row: Any) -> dict[str, Any]:
    subjects = _row_value(row, "subjects", [])
    if isinstance(subjects, str):
        subjects_value = [part.strip() for part in subjects.split(",") if part.strip()]
    elif isinstance(subjects, list):
        subjects_value = [str(subject).strip() for subject in subjects if str(subject).strip()]
    else:
        subjects_value = []

    min_score = _int_value(_row_value(row, "min_score", _row_value(row, "passing_score", 0)))
    min_score_is_valid = is_valid_score(min_score)
    min_score_is_suspicious = is_suspicious_score(min_score)
    study_form = normalize_study_form(_row_value(row, "study_form", ""))
    full_name = _string_value(
        _row_value(row, "university_full_name", _row_value(row, "university_name", _row_value(row, "university", "")))
    )
    short_name = normalize_short_name_display(_row_value(row, "university_short_name", ""), full_name)
    raw_university = _string_value(_row_value(row, "university", full_name))
    admission_type = _string_value(_row_value(row, "admission_type", _row_value(row, "type", "")))
    row_type = normalize_type(admission_type) or "бюджет"
    financing = financing_label(row_type)
    study_form_label = normalize_study_form(_row_value(row, "study_form", ""))
    contest = contest_label(admission_type)

    return {
        "university": get_university_display_name(full_name, short_name, raw_university),
        "city": _string_value(_row_value(row, "city", "")),
        "region": _string_value(_row_value(row, "region", "")),
        "program": _string_value(_row_value(row, "program", _row_value(row, "direction_name", ""))),
        "direction": _string_value(_row_value(row, "direction", _row_value(row, "direction_name", ""))),
        "profile": _string_value(_row_value(row, "profile", "")),
        "direction_code": _string_value(_row_value(row, "direction_code", _row_value(row, "code", ""))),
        "subjects": subjects_value,
        "min_score": min_score,
        "score_is_valid": min_score_is_valid,
        "score_is_suspicious": min_score_is_suspicious,
        "score_display": score_display(min_score),
        "score_note": score_note(min_score),
        "type": row_type,
        "financing_label": financing,
        "url": _string_value(_row_value(row, "url", _row_value(row, "website", ""))),
        "price": _row_value(row, "price", None),
        "study_form": study_form,
        "study_form_label": study_form_label,
        "duration": _string_value(_row_value(row, "duration", "")),
        "note": _string_value(_row_value(row, "note", "")),
        "year": _row_value(row, "year", _row_value(row, "latest_year", None)),
        "faculty": _string_value(_row_value(row, "faculty", _row_value(row, "faculty_name", ""))),
        "admission_type": admission_type,
        "admission_type_label": admission_type_label(admission_type),
        "contest_label": contest,
        "university_short_name": short_name,
        "university_full_name": full_name,
        "source": _string_value(_row_value(row, "source", "postgresql")),
        "match_quality": _string_value(_row_value(row, "match_quality", "")),
        "match_reason": _string_value(_row_value(row, "match_reason", _row_value(row, "match_quality", ""))),
    }


def with_display_labels(item: Mapping[str, Any]) -> dict[str, Any]:
    record = dict(item)
    financing = financing_label(record.get("financing_label") or record.get("type") or record.get("admission_type"))
    study_form = normalize_study_form(record.get("study_form_label") or record.get("study_form", ""))
    contest = contest_label(record.get("contest_label") or record.get("admission_type_label") or record.get("admission_type"))

    record["financing_label"] = financing
    record["study_form_label"] = study_form
    record["contest_label"] = contest
    min_score = _min_score(record)
    record["score_is_valid"] = is_valid_score(min_score)
    record["score_is_suspicious"] = is_suspicious_score(min_score)
    record["score_display"] = score_display(min_score)
    record["score_note"] = score_note(min_score)
    return record


def normalize_study_form(value: Any) -> str:
    normalized = normalize(value)
    if not normalized:
        return ""
    return STUDY_FORM_LABELS.get(normalized, str(value).strip())


def postgres_study_form(value: Any) -> str | None:
    return POSTGRES_STUDY_FORMS.get(normalize(value))


def postgres_admission_types(value: Any) -> list[str]:
    return POSTGRES_ADMISSION_BY_API_TYPE.get(normalize_type(value), [])


def postgres_admission_type_values(value: Any) -> list[str]:
    return POSTGRES_ADMISSION_BY_LABEL.get(normalize(value), [])


def postgres_direction_terms(value: str) -> list[str]:
    return direction_search_terms(value)


def direction_search_terms(value: Any) -> list[str]:
    raw_value = str(value or "").strip()
    requested = normalize_direction(raw_value)
    if not requested:
        return []

    code_stripped = DIRECTION_CODE_RE.sub(" ", raw_value)
    code_stripped = " ".join(code_stripped.split())
    terms = {requested, raw_value, code_stripped}
    for direction, synonyms in DIRECTION_SYNONYMS.items():
        if normalize_direction(requested) == direction or normalize(requested) == normalize(direction):
            terms.add(direction)
            terms.update(synonyms)

    preset = POSTGRES_DIRECTION_PRESETS.get(requested)
    if preset:
        terms.update(preset)

    result = []
    for term in terms:
        cleaned = " ".join(str(term).strip().split())
        if cleaned and cleaned not in result:
            result.append(cleaned)
    return result[:24]


def direction_code_terms(value: Any) -> list[str]:
    return _dedupe_text(DIRECTION_CODE_RE.findall(str(value or "")))


def region_search_terms(value: Any) -> list[str]:
    raw = str(value or "").strip()
    if not raw:
        return []

    normalized_region = normalize_region(raw)
    terms = {raw, normalized_region}
    for alias in (normalize(raw), normalize(normalized_region)):
        terms.update(REGION_ALIAS_GROUPS.get(alias, []))
    return _dedupe_text(terms)


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

    sort = str(filters.get("sort", ""))
    score = filters.get("score")
    score_order_param = ""
    if score is not None:
        max_score = add_param(int(score) + AMBITIOUS_SCORE_MARGIN)
        where_parts.append(f"ps.min_score <= {max_score}")
        if _postgres_order_uses_score_closeness(sort):
            score_order_param = add_param(int(score))

    match_select_sql = _postgres_match_select(filters, add_param)
    order_sql = _postgres_order_by(sort, score is not None, score_order_param)
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
            u.name AS university,
            u.name AS university_name,
            u.name AS university_full_name,
            u.short_name AS university_short_name,
            u.city,
            u.region,
            u.website AS url,
            d.name AS program,
            d.name AS direction,
            d.code AS direction_code,
            d.profile,
            d.study_form::TEXT AS study_form,
            f.name AS faculty,
            ps.year,
            ps.admission_type::TEXT AS admission_type,
            ps.min_score,
            ps.note,
            'postgresql' AS source,
            {match_select_sql}
        FROM latest_scores ps
        JOIN directions d ON d.id = ps.direction_id
        JOIN universities u ON u.id = d.university_id
        LEFT JOIN faculties f ON f.id = d.faculty_id
        WHERE {where_sql}
        ORDER BY match_rank ASC, {order_sql}
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


def _postgres_match_select(filters: Mapping[str, Any], add_param: Any) -> str:
    direction_value = str(filters.get("direction", "") or "")
    if not normalize(direction_value):
        return "'' AS match_quality, 9 AS match_rank"

    if filters.get("_direction_match_mode") == "exact_code" and direction_code_terms(direction_value):
        return "'exact_code' AS match_quality, 0 AS match_rank"

    if _is_direction_alias(direction_value):
        return "'alias_category' AS match_quality, 2 AS match_rank"

    exact_terms = [normalize(term) for term in postgres_direction_terms(direction_value) if normalize(term)]
    if not exact_terms:
        return "'broad_match' AS match_quality, 5 AS match_rank"

    exact_param = add_param(exact_terms[:8])
    return (
        "CASE "
        f"WHEN lower(d.name) = ANY({exact_param}::TEXT[]) THEN 'exact_name' "
        f"WHEN lower(COALESCE(d.profile, '')) = ANY({exact_param}::TEXT[]) THEN 'exact_profile' "
        "WHEN COALESCE(d.profile, '') <> '' THEN 'profile_match' "
        "ELSE 'broad_match' "
        "END AS match_quality, "
        "CASE "
        f"WHEN lower(d.name) = ANY({exact_param}::TEXT[]) THEN 1 "
        f"WHEN lower(COALESCE(d.profile, '')) = ANY({exact_param}::TEXT[]) THEN 1 "
        "WHEN COALESCE(d.profile, '') <> '' THEN 3 "
        "ELSE 4 "
        "END AS match_rank"
    )


def _is_direction_alias(value: Any) -> bool:
    requested = normalize_direction(str(value or ""))
    normalized_requested = normalize(requested)
    if requested in POSTGRES_DIRECTION_PRESETS:
        return True
    for direction, synonyms in DIRECTION_SYNONYMS.items():
        if normalize(direction) == normalized_requested:
            return True
        if any(normalize(synonym) == normalized_requested for synonym in synonyms):
            return True
    return False


def _append_postgres_common_filters(
    where_parts: list[str],
    params: list[Any],
    filters: Mapping[str, Any],
    include_direction: bool = True,
) -> None:
    def add_param(value: Any) -> str:
        params.append(value)
        return f"${len(params)}"

    if not filters.get("include_synthetic"):
        where_parts.append(
            "NOT ("
            "u.name ILIKE '%Региональный центр технологий и инженерии%' "
            "OR u.name ILIKE '%Институт социальных и цифровых профессий%' "
            "OR COALESCE(u.short_name, '') ~* '^(РЦТИ|ИСЦП)-[0-9]+$'"
            ")"
        )

    if filters.get("region"):
        region_conditions = []
        for term in region_search_terms(filters["region"]):
            region_pattern = add_param(f"%{term}%")
            region_conditions.append(f"u.region ILIKE {region_pattern}")
        where_parts.append("(" + " OR ".join(region_conditions) + ")")

    if filters.get("city"):
        city_pattern = add_param(f"%{filters['city']}%")
        where_parts.append(f"u.city ILIKE {city_pattern}")

    admission_types = postgres_admission_types(filters.get("type", ""))
    if admission_types:
        admission_param = add_param(admission_types)
        where_parts.append(f"ps.admission_type::TEXT = ANY({admission_param}::TEXT[])")
    elif normalize(filters.get("type", "")):
        where_parts.append("FALSE")

    exact_admission_types = postgres_admission_type_values(filters.get("admission_type", ""))
    if exact_admission_types:
        admission_type_param = add_param(exact_admission_types)
        where_parts.append(f"ps.admission_type::TEXT = ANY({admission_type_param}::TEXT[])")
    elif normalize(filters.get("admission_type", "")):
        where_parts.append("FALSE")

    study_form = postgres_study_form(filters.get("study_form", ""))
    if study_form:
        study_form_param = add_param(study_form)
        where_parts.append(f"d.study_form::TEXT = {study_form_param}")
    elif normalize(filters.get("study_form", "")):
        where_parts.append("FALSE")

    if include_direction:
        direction_value = str(filters.get("direction", "") or "")
        code_terms = direction_code_terms(direction_value)
        if filters.get("_direction_match_mode") == "exact_code":
            if code_terms:
                code_param = add_param(code_terms)
                where_parts.append(f"COALESCE(d.code, '') = ANY({code_param}::TEXT[])")
            elif normalize(direction_value):
                where_parts.append("FALSE")
        else:
            direction_terms = postgres_direction_terms(direction_value)
            code_terms = direction_code_terms(direction_value)
            if direction_terms:
                direction_conditions = []
                for term in direction_terms:
                    term_param = add_param(f"%{term}%")
                    direction_conditions.append(
                        "("
                        f"d.name ILIKE {term_param} "
                        f"OR COALESCE(d.profile, '') ILIKE {term_param}"
                        ")"
                    )
                for code in code_terms:
                    code_param = add_param(code)
                    direction_conditions.append(f"COALESCE(d.code, '') = {code_param}")
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
            f"OR COALESCE(d.code, '') ILIKE {q_param} "
            f"OR d.name ILIKE {q_param} "
            f"OR COALESCE(d.profile, '') ILIKE {q_param} "
            f"OR COALESCE(f.name, '') ILIKE {q_param}"
            ")"
        )


def _postgres_order_by(sort: str, has_score: bool, score_param: str = "") -> str:
    if sort == "min_score_desc":
        return (
            f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, "
            "ps.min_score DESC NULLS LAST, ps.year DESC NULLS LAST, u.name ASC, d.name ASC"
        )
    if sort == "university":
        return f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, u.name ASC, d.name ASC, ps.year DESC NULLS LAST"
    if sort == "city":
        return f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, u.city ASC NULLS LAST, u.name ASC, d.name ASC"
    if sort == "direction":
        return f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, d.name ASC, u.name ASC, ps.year DESC NULLS LAST"
    if sort == "year_desc":
        return f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, ps.year DESC NULLS LAST, u.name ASC, d.name ASC"
    if sort == "min_score_asc":
        return f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, ps.min_score ASC NULLS LAST, ps.year DESC NULLS LAST, u.name ASC, d.name ASC"
    if has_score and score_param:
        return (
            f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, "
            f"CASE WHEN ps.min_score <= {score_param} THEN 0 ELSE 1 END ASC, "
            f"ABS(ps.min_score - {score_param}) ASC, "
            "ps.year DESC NULLS LAST, u.name ASC, d.name ASC"
        )
    return f"(ps.min_score >= {MIN_REASONABLE_SCORE}) DESC, u.name ASC, d.name ASC, ps.year DESC NULLS LAST"


def _postgres_order_uses_score_closeness(sort: str) -> bool:
    return sort not in {"min_score_asc", "min_score_desc", "university", "city", "direction", "year_desc"}


def _sort_json_universities(rows: list[dict[str, Any]], sort: str) -> list[dict[str, Any]]:
    if sort == "min_score_asc":
        return sorted(rows, key=lambda item: (not is_valid_score(_min_score(item)), is_suspicious_score(_min_score(item)), _min_score(item) or 0))
    if sort == "min_score_desc":
        return sorted(rows, key=lambda item: (not is_valid_score(_min_score(item)), is_suspicious_score(_min_score(item)), -(_min_score(item) or 0)))
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
    requested_terms = region_search_terms(requested)
    item_region = normalize_region(str(value or ""))
    normalized_region = normalize(item_region)
    return any(normalize(term) == normalized_region or _text_matches(item_region, term) for term in requested_terms)


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


def admission_type_label(value: Any) -> str:
    normalized = normalize(value).replace(" ", "_").replace("-", "_")
    return ADMISSION_TYPE_LABELS.get(normalized, str(value).strip() if value is not None else "")


def financing_label(value: Any) -> str:
    return normalize_type(value)


def contest_label(value: Any) -> str:
    normalized = normalize(value).replace(" ", "_").replace("-", "_")
    return CONTEST_LABELS.get(normalized, str(value).strip() if has_display_text(value) else "")


def achievement_category(code: str) -> str:
    normalized = normalize(code)
    if "gto" in normalized:
        return "спорт"
    if "olympiad" in normalized or "vsosh" in normalized:
        return "олимпиады"
    if "volunteer" in normalized:
        return "волонтёрство"
    if "medal" in normalized or "diploma" in normalized or "sochinenie" in normalized:
        return "аттестат"
    return "прочее"


def is_technical_university_name(value: Any) -> bool:
    text = _string_value(value)
    normalized = text.upper().replace("Ё", "Е")
    if not text or normalized in KNOWN_UNIVERSITY_ABBREVIATIONS:
        return False
    if TECHNICAL_UNIVERSITY_RE.match(text):
        return True
    if any(char.isdigit() for char in text):
        return True
    return len(text) <= 2 and text.upper() == text and any(char.isalpha() for char in text)


def is_synthetic_university_name(value: Any) -> bool:
    normalized = normalize(value)
    return any(marker in normalized for marker in SYNTHETIC_UNIVERSITY_NAME_MARKERS)


def is_synthetic_university_record(record: Mapping[str, Any]) -> bool:
    name_values = (
        record.get("university_full_name"),
        record.get("university_name"),
        record.get("university"),
        record.get("name"),
    )
    if any(is_synthetic_university_name(value) for value in name_values):
        return True

    short_name = _string_value(record.get("university_short_name", record.get("short_name", "")))
    return bool(short_name and SYNTHETIC_UNIVERSITY_SHORT_NAME_RE.match(short_name))


def has_display_text(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def normalize_short_name_display(value: Any, full_name: Any = "") -> str:
    text = _string_value(value)
    if not is_useful_short_name(text, full_name):
        return ""
    normalized = " ".join(text.split())
    return normalized.upper().replace("Ё", "Е")


def is_useful_short_name(value: Any, full_name: Any = "") -> bool:
    text = _string_value(value)
    if not text:
        return False
    if is_synthetic_university_record({"university_short_name": text}):
        return False
    if full_name and normalize(text) == normalize(full_name):
        return False
    normalized = text.upper().replace("Ё", "Е")
    if normalized in KNOWN_UNIVERSITY_ABBREVIATIONS:
        return True
    if is_technical_university_name(text):
        return False
    compact = normalized.replace(" ", "").replace(".", "")
    if any(char.isdigit() for char in compact):
        return False
    letters_count = sum(1 for char in compact if char.isalpha())
    return 2 <= letters_count <= 16 and len(normalized) <= 24


def format_direction_directory_item(name: Any, code: Any = "", profile: Any = "") -> str:
    name_text = _string_value(name)
    code_text = _string_value(code)
    profile_text = _string_value(profile)
    if code_text and name_text:
        if normalize(name_text).startswith(normalize(code_text)):
            return name_text
        return f"{code_text} {name_text}"
    if code_text and profile_text:
        if normalize(profile_text).startswith(normalize(code_text)):
            return profile_text
        return f"{code_text} {profile_text}"
    if profile_text and name_text and normalize(profile_text) != normalize(name_text):
        return f"{name_text} — {profile_text}"
    return name_text or profile_text or code_text


def get_university_display_name(full_name: Any, short_name: Any = "", fallback: Any = "") -> str:
    full_text = _string_value(full_name)
    short_text = normalize_short_name_display(short_name, full_text)
    fallback_text = _string_value(fallback)
    for candidate in (full_text, fallback_text, short_text):
        if candidate and not is_technical_university_name(candidate):
            return candidate
    return full_text or fallback_text or short_text or "Вуз"


def _term_matches_haystack(term: str, normalized_haystack: str) -> bool:
    normalized_term = normalize(term)
    if not normalized_term:
        return False
    if normalized_term in normalized_haystack:
        return True
    parts = [part for part in normalized_term.split() if part]
    return len(parts) > 1 and all(part in normalized_haystack for part in parts)


def _dedupe_text(values: Any) -> list[str]:
    result = []
    for value in values:
        text = _string_value(value)
        if text and text not in result:
            result.append(text)
    return result
