from typing import Any


RESULT_PAGE_SIZE = 5
SEARCH_FETCH_LIMIT = 200


def result_page(
    results: list[dict[str, Any]],
    start_index: int = 1,
) -> tuple[list[dict[str, Any]], int, int, bool]:
    start_index = max(1, start_index)
    start_offset = start_index - 1
    page_results = results[start_offset:start_offset + RESULT_PAGE_SIZE]
    if not page_results:
        return [], start_index, start_offset, False

    page_end = start_offset + len(page_results)
    return page_results, start_index, page_end, page_end < len(results)


def format_page_notice(start_index: int, end_index: int, total_count: int) -> str:
    return f"Показаны варианты {start_index}–{end_index} из {total_count}."
