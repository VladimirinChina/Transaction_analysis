import pytest
from src.reports import get_expenses_summary


@pytest.fixture
def transactions_data() -> list[dict]:
    """Фикстура с разнообразными транзакциями для тестирования отчета."""
    return [
        {"amount": -1000, "category": "Еда"},
        {"amount": -2000, "category": "Еда"},
        {"amount": -500, "category": "Транспорт"},
        {"amount": -300, "category": "Наличные"},
        {"amount": -700, "category": "Переводы"},
        {"amount": 1000, "category": "Доход"},  # Должно игнорироваться (положительное)
        {"amount": -100, "category": "Спорт"},
        {"amount": -100, "category": "Кино"},
        {"amount": -100, "category": "Связь"},
        {"amount": -100, "category": "Аптеки"},
        {"amount": -100, "category": "Дом"},
        {"amount": -100, "category": "Книги"},
        {"amount": -50, "category": "Подарки"},
    ]


def test_expenses_summary_basic(transactions_data: list[dict]) -> None:
    """Проверка базовых расчетов суммы и фильтрации доходов."""
    result = get_expenses_summary(transactions_data)

    # Сумма всех отрицательных: 1000+2000+500+300+700+100*6+50 = 5150
    assert result["total_amount"] == 5150
    # Доход (1000) не должен попасть в расходы
    assert all(item["amount"] > 0 for item in result["main"])


def test_expenses_summary_special_categories(transactions_data: list[dict]) -> None:
    """Проверка выделения 'Наличных' и 'Переводов' в отдельный список."""
    result = get_expenses_summary(transactions_data)

    special_categories = [item["category"] for item in result["transfers_and_cash"]]
    assert "Наличные" in special_categories
    assert "Переводы" in special_categories

    # Проверяем, что их нет в основном списке main
    main_categories = [item["category"] for item in result["main"]]
    assert "Наличные" not in main_categories
    assert "Переводы" not in main_categories


def test_expenses_summary_top_and_others(transactions_data: list[dict]) -> None:
    """Проверка ограничения ТОП-7 и наличия категории 'Остальное'."""
    result = get_expenses_summary(transactions_data)

    # В main должны быть 7 категорий + 1 "Остальное"
    assert len(result["main"]) == 8
    assert result["main"][-1]["category"] == "Остальное"

    # Проверка сортировки: Еда (3000) должна быть первой
    assert result["main"][0]["category"] == "Еда"
    assert result["main"][0]["amount"] == 3000


def test_expenses_summary_empty() -> None:
    """Проверка работы с пустыми данными."""
    result = get_expenses_summary([])
    assert result["total_amount"] == 0
    assert result["main"] == []
    assert result["transfers_and_cash"] == []
