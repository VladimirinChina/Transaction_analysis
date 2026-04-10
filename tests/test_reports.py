import pytest
import json
import pandas as pd
from typing import Any, Dict, List

from src.reports import spending_by_category, get_expenses_summary
from unittest.mock import patch, mock_open


@pytest.fixture
def transactions_data() -> List[Dict]:
    """Фикстура с разнообразными транзакциями для тестирования отчета."""
    return [
        {"date": "2024-03-01", "amount": -1000, "category": "Еда"},
        {"date": "2024-03-05", "amount": -2000, "category": "Еда"},
        {"date": "2024-03-10", "amount": -500, "category": "Транспорт"},
        {"date": "2024-03-15", "amount": -300, "category": "Наличные"},
        {"date": "2024-03-20", "amount": -700, "category": "Переводы"},
        {"date": "2024-03-25", "amount": 1000, "category": "Доход"},
        {"date": "2024-03-26", "amount": -100, "category": "Спорт"},
        {"date": "2024-03-27", "amount": -100, "category": "Кино"},
        {"date": "2024-03-28", "amount": -100, "category": "Связь"},
        {"date": "2024-03-29", "amount": -100, "category": "Аптеки"},
        {"date": "2024-03-30", "amount": -100, "category": "Дом"},
        {"date": "2024-03-31", "amount": -100, "category": "Книги"},
        {"date": "2024-03-31", "amount": -50, "category": "Подарки"},
    ]


@pytest.fixture
def transactions_df(transactions_data: List[Dict]) -> pd.DataFrame:
    """Создает DataFrame из фикстуры выше."""
    return pd.DataFrame(transactions_data)


# Добавлен патч, чтобы при запуске тестов не создавались реальные файлы
@patch("builtins.open", new_callable=mock_open)
def test_spending_by_category_basic(mock_file: Any) -> None:
    df = pd.DataFrame([
        {"date": "2024-01-10", "category": "Еда", "amount": -100},
        {"date": "2024-02-10", "category": "Еда", "amount": -200},
        {"date": "2024-03-10", "category": "Транспорт", "amount": -50},
    ])

    result = spending_by_category(df, "Еда", "2024-03-15")
    data = json.loads(result)

    assert data["total_spent"] == 300
    assert data["transactions_count"] == 2
    mock_file.assert_called()  # Проверка, что декоратор сработал


@pytest.mark.parametrize(
    "category, expected",
    [
        ("Еда", 300),
        ("Транспорт", 50),
        ("Развлечения", 0),
    ]
)
@patch("builtins.open", new_callable=mock_open)
def test_spending_by_category_param(mock_file: Any, category: str, expected: int) -> None:
    df = pd.DataFrame([
        {"date": "2024-01-10", "category": "Еда", "amount": -100},
        {"date": "2024-02-10", "category": "Еда", "amount": -200},
        {"date": "2024-03-10", "category": "Транспорт", "amount": -50},
    ])

    result = spending_by_category(df, category, "2024-03-15")
    data = json.loads(result)

    assert data["total_spent"] == expected
    mock_file.assert_called()


@patch("builtins.open", new_callable=mock_open)
def test_spending_by_category_date_filter(mock_file: Any) -> None:
    df = pd.DataFrame([
        {"date": "2023-01-10", "category": "Еда", "amount": -100},  # вне диапазона (больше 90 дней)
        {"date": "2024-02-10", "category": "Еда", "amount": -200},
    ])

    result = spending_by_category(df, "Еда", "2024-03-15")
    data = json.loads(result)

    assert data["total_spent"] == 200
    mock_file.assert_called()


@patch("builtins.open", new_callable=mock_open)
def test_spending_by_category_with_fixture(mock_file: Any, transactions_df: pd.DataFrame) -> None:
    """Тест использует данные из фикстуры."""
    result = spending_by_category(transactions_df, "Еда", "2024-04-01")
    data = json.loads(result)

    # В фикстуре две транзакции по еде: -1000 и -2000
    assert data["total_spent"] == 3000
    mock_file.assert_called()


def test_expenses_summary_basic(transactions_data: List[Dict]) -> None:
    """Проверка базовых расчетов суммы и фильтрации доходов."""
    result = get_expenses_summary(transactions_data)

    # Сумма всех отрицательных: 1000+2000+500+300+700+100*6+50 = 5150
    assert result["total_amount"] == 5150
    # Доход (1000) не должен попасть в расходы
    assert all(item["amount"] > 0 for item in result["main"])


def test_expenses_summary_special_categories(transactions_data: List[Dict]) -> None:
    """Проверка выделения 'Наличных' и 'Переводов' в отдельный список."""
    result = get_expenses_summary(transactions_data)

    special_categories = [item["category"] for item in result["transfers_and_cash"]]
    assert "Наличные" in special_categories
    assert "Переводы" in special_categories

    # Проверяем, что их нет в основном списке main
    main_categories = [item["category"] for item in result["main"]]
    assert "Наличные" not in main_categories
    assert "Переводы" not in main_categories


def test_expenses_summary_top_and_others(transactions_data: List[Dict]) -> None:
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
