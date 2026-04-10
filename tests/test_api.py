from unittest.mock import patch, MagicMock
from src.utils import get_currency_rates


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "rates": {
            "USD": 90.0,
            "EUR": 100.0
        }
    }

    result = get_currency_rates(["USD", "EUR"])

    assert result == [
        {"currency": "USD", "rate": 90.0},
        {"currency": "EUR", "rate": 100.0}
    ]
