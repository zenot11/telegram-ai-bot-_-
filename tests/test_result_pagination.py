from telegram_bot.services.result_pagination import format_page_notice, result_page


def test_result_page_splits_results_by_five() -> None:
    items = [{"id": index} for index in range(1, 13)]

    first, first_start, first_end, first_more = result_page(items)
    second, second_start, second_end, second_more = result_page(items, 6)
    third, third_start, third_end, third_more = result_page(items, 11)

    assert [item["id"] for item in first] == [1, 2, 3, 4, 5]
    assert (first_start, first_end, first_more) == (1, 5, True)
    assert [item["id"] for item in second] == [6, 7, 8, 9, 10]
    assert (second_start, second_end, second_more) == (6, 10, True)
    assert [item["id"] for item in third] == [11, 12]
    assert (third_start, third_end, third_more) == (11, 12, False)


def test_format_page_notice_uses_global_numbers() -> None:
    assert format_page_notice(6, 10, 12) == "Показаны варианты 6–10 из 12."
