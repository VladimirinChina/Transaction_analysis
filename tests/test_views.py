import json
from unittest.mock import patch, MagicMock
from src.views import get_events_page


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.filter_by_period")
@patch("src.views.read_operations")
@patch("src.views.load_user_settings")
def test_get_events_page_success(
        mock_settings: MagicMock,
        mock_read: MagicMock,
        mock_filter: MagicMock,
        mock_currency: MagicMock,
        mock_stocks: MagicMock,
) -> None:
    """Проверка формирования страницы при корректных данных."""

    # 1. Настраиваем возвращаемые значения
    mock_read.return_value = [
        {"amount": -1000, "category": "Еда"},
        {"amount": 2000, "category": "Зарплата"},
    ]
    mock_filter.return_value = mock_read.return_value
    mock_currency.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]
    mock_settings.return_value = {
        "user_currencies": ["USD"],
        "user_stocks": ["AAPL"]
    }

    # 2. Вызываем функцию
    result_json = get_events_page("20.05.2024")
    data = json.loads(result_json)

    # 3. Проверки структуры
    assert "expenses" in data
    assert "income" in data
    assert "currency_rates" in data
    assert "stock_prices" in data

    # 4. Проверка данных
    assert data["currency_rates"][0]["currency"] == "USD"
    assert data["stock_prices"][0]["stock"] == "AAPL"
    assert data["expenses"]["total_amount"] == 1000
    assert data["income"]["total_amount"] == 2000


def test_get_events_page_empty() -> None:
    """Проверка работы страницы при отсутствии данных (пустые списки)."""
    with patch("src.views.read_operations", return_value=[]), \
            patch("src.views.filter_by_period", return_value=[]), \
            patch("src.views.get_currency_rates", return_value=[]), \
            patch("src.views.get_stock_prices", return_value=[]), \
            patch("src.views.load_user_settings", return_value={"user_currencies": [], "user_stocks": []}):
        result = get_events_page("20.05.2024")
        data = json.loads(result)

        assert data["expenses"]["total_amount"] == 0
        assert data["income"]["total_amount"] == 0
        assert data["currency_rates"] == []


def test_get_events_page_error_handling() -> None:
    """Проверка, что функция не падает при критической ошибке в расчетах."""
    # Имитируем падение одной из функций, например, read_operations
    with patch("src.views.read_operations", side_effect=Exception("Database error")):
        result_json = get_events_page("20.05.2024")
        data = json.loads(result_json)

        # Проверяем, что вернулся JSON с ошибкой, а не поднялось исключение
        assert "error" in data
        assert data["error"] == "Internal server error"
