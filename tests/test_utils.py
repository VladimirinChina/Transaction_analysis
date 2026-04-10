import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd
from src.utils import read_operations, filter_by_period
from src.utils import get_stock_prices
from src.utils import get_currency_rates
# Тесты для read_operations с использованием mock


@patch("pandas.read_excel")
def test_read_operations_mock(mock_read: MagicMock) -> None:
    """Тестируем чтение файла, имитируя работу pandas."""
    # Создаем тестовый DataFrame, который якобы вернул pandas
    mock_df = pd.DataFrame({
        "Дата операции": ["01.01.2024", "02.01.2024"],
        "Номер карты": ["*1111", "*2222"],
        "Сумма операции с округлением": [100.5, 200.0],
        "Категория": ["Еда", "Транспорт"],
        "Описание": ["Магнит", "Такси"],
        "Лишний столбец": ["удалить", "меня"]
    })
    mock_read.return_value = mock_df

    # Вызываем функцию
    data = read_operations("fake_path.xlsx")

    # Проверяем результат
    assert len(data) == 2
    assert data[0]["amount"] == 100.5
    assert "date" in data[0]
    assert "Лишний столбец" not in data[0]  # Проверка, что фильтр столбцов работает
    mock_read.assert_called_once_with("fake_path.xlsx")


# Тесты для filter_by_period

@pytest.fixture
def sample_data() -> list[dict]:
    """Фикстура с данными для тестов фильтрации."""
    return [
        {"date": datetime(2024, 5, 15), "amount": 100},  # Май
        {"date": datetime(2024, 5, 1), "amount": 50},    # Начало мая
        {"date": datetime(2024, 4, 30), "amount": 200},  # Апрель
        {"date": datetime(2023, 5, 15), "amount": 300},  # Прошлый год
    ]


def test_filter_by_month(sample_data: list[dict]) -> None:
    """Тест фильтрации за месяц."""
    result = filter_by_period(sample_data, "20.05.2024", "M")
    assert len(result) == 2
    for item in result:
        assert item["date"].month == 5
        assert item["date"].year == 2024


def test_filter_by_year(sample_data: list[dict]) -> None:
    """Тест фильтрации за год."""
    result = filter_by_period(sample_data, "31.12.2024", "Y")

    assert len(result) == 3  # Все за 2024 до конца декабря
    assert all(item["date"].year == 2024 for item in result)


def test_filter_by_period_invalid_mode(sample_data: list[dict]) -> None:
    """Проверка вызова ошибки при неверном периоде."""
    with pytest.raises(ValueError, match="Invalid period"):
        filter_by_period(sample_data, "20.05.2024", "QUARTER")


def test_filter_by_period_empty_list() -> None:
    """Проверка работы с пустым списком."""
    result = filter_by_period([], "20.05.2024", "M")
    assert result == []


def test_filter_by_all_time(sample_data: list[dict]) -> None:
    """Тест периода ALL."""
    result = filter_by_period(sample_data, "20.05.2024", "ALL")
    assert len(result) == 4


@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "Global Quote": {
            "05. price": "150.00"
        }
    }

    result = get_stock_prices(["AAPL"])

    assert result == [
        {"stock": "AAPL", "price": 150.0}
    ]


@patch("src.utils.requests.get")
def test_get_currency_rates_empty(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {"rates": {}}

    result = get_currency_rates(["USD"])

    assert result == []
