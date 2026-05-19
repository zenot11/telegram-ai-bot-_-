import json
from pathlib import Path
from typing import Any

from telegram_bot.services.validation import education_type_label, normalize_education_type


DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "universities.json"

REQUIRED_FIELDS = {
    "university",
    "city",
    "region",
    "program",
    "direction",
    "subjects",
    "min_score",
    "type",
    "url",
}

OPTIONAL_STRING_FIELDS = {
    "study_form",
    "duration",
    "note",
}


class DataLoadError(ValueError):
    """Raised when universities data cannot be loaded or validated."""


def get_universities_data_path() -> Path:
    return DEFAULT_DATA_PATH


def load_universities(path: str | Path | None = None) -> list[dict[str, Any]]:
    data_path = Path(path) if path is not None else get_universities_data_path()
    try:
        raw_data = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise DataLoadError(f"Data file not found: {data_path}") from error
    except json.JSONDecodeError as error:
        raise DataLoadError(f"Data file is not valid JSON: {data_path}: {error}") from error

    errors = validate_universities_data(raw_data)
    if errors:
        raise DataLoadError("Universities data validation failed:\n" + "\n".join(errors))

    return [normalize_university_record(record) for record in raw_data]


def validate_universities_data(data: object) -> list[str]:
    if not isinstance(data, list):
        return ["Data must be a JSON array of university records"]
    if not data:
        return ["Data must contain at least one university record"]

    errors: list[str] = []
    for index, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            errors.append(f"Record #{index}: must be an object")
            continue
        errors.extend(validate_university_record(record, index))
    return errors


def validate_university_record(record: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []

    for field in sorted(REQUIRED_FIELDS):
        if field not in record:
            errors.append(f'Record #{index}: missing required field "{field}"')

    for field in ("university", "city", "region", "program", "direction", "url"):
        if field in record and not _is_non_empty_string(record[field]):
            errors.append(f'Record #{index}: "{field}" must be non-empty string')

    subjects = record.get("subjects")
    if "subjects" in record:
        if not isinstance(subjects, list):
            errors.append(f'Record #{index}: "subjects" must be list of strings')
        elif not all(isinstance(subject, str) and subject.strip() for subject in subjects):
            errors.append(f'Record #{index}: "subjects" must be list of strings')

    if "min_score" in record and not _is_integer(record.get("min_score")):
        errors.append(f'Record #{index}: "min_score" must be integer')

    if "type" in record and _normalize_type(record.get("type")) is None:
        errors.append(f'Record #{index}: "type" must be "бюджет" or "платное"')

    if "price" in record and not (
        record["price"] is None or isinstance(record["price"], str) or _is_integer(record["price"])
    ):
        errors.append(f'Record #{index}: "price" must be string, integer or null')

    for field in OPTIONAL_STRING_FIELDS:
        if field in record and record[field] is not None and not isinstance(record[field], str):
            errors.append(f'Record #{index}: "{field}" must be string')

    return errors


def normalize_university_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(record)
    for field in ("university", "city", "region", "program", "direction", "url"):
        if isinstance(normalized.get(field), str):
            normalized[field] = normalized[field].strip()

    if isinstance(normalized.get("subjects"), list):
        normalized["subjects"] = [
            subject.strip()
            for subject in normalized["subjects"]
            if isinstance(subject, str) and subject.strip()
        ]

    normalized_type = _normalize_type(normalized.get("type"))
    if normalized_type:
        normalized["type"] = normalized_type

    for field in OPTIONAL_STRING_FIELDS:
        if isinstance(normalized.get(field), str):
            normalized[field] = normalized[field].strip()

    return normalized


def _normalize_type(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = normalize_education_type(value)
    if normalized:
        return education_type_label(normalized)
    return None


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
