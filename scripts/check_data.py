#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_stub.data_loader import get_universities_data_path, load_universities, validate_universities_data  # noqa: E402


def main() -> int:
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else get_universities_data_path()
    try:
        raw_data = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Data check failed.\nFile not found: {data_path}")
        return 1
    except json.JSONDecodeError as error:
        print(f"Data check failed.\nInvalid JSON: {error}")
        return 1

    errors = validate_universities_data(raw_data)
    if errors:
        print("Data check failed.")
        for error in errors:
            print(error)
        return 1

    rows = load_universities(data_path)
    stats = _stats(rows)
    print("Data check passed.")
    print(f"Records: {len(rows)}")
    print(f"Regions: {len(stats['regions'])}")
    print(f"Directions: {len(stats['directions'])}")
    print(f"Types: budget={stats['budget']}, paid={stats['paid']}")
    return 0


def _stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "regions": {str(item.get("region", "")).strip() for item in rows if item.get("region")},
        "directions": {str(item.get("direction", "")).strip() for item in rows if item.get("direction")},
        "budget": sum(1 for item in rows if item.get("type") == "бюджет"),
        "paid": sum(1 for item in rows if item.get("type") == "платное"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
