import json
from typing import List, Dict, Any

import pytest
from src.services import find_transactions_by_phone


@pytest.mark.parametrize("description, expected_count", [
    # Стандартные форматы
    ("Перевод по номеру +79991234567", 1),
    ("Оплата 89991234567", 1),
    ("Номер телефона 79991234567", 1),

    # Форматы с разделителями
    ("Контакт: +7 999 123 45 67", 1),
    ("Служба поддержки: 8-999-123-45-67", 1),
    ("Мама: +7(999)123-45-67", 1),

    # Несколько номеров или отсутствие
    ("Покупка в магазине (без номера)", 0),
    ("Два номера +79991112233 и 89001112233", 1),  # Наша функция вернет 1 транзакцию
    ("", 0),
])
def test_find_transactions_by_phone_parameterized(description: str, expected_count: int) -> None:
    """
    Параметризованный тест для проверки различных форматов номеров телефонов.
    """
    transactions = [
        {"description": description, "amount": -100}
    ]

    result_json = find_transactions_by_phone(transactions)
    result = json.loads(result_json)

    assert len(result) == expected_count


def test_find_transactions_by_phone_empty_list() -> None:
    """Проверка работы с пустым списком транзакций."""
    assert find_transactions_by_phone([]) == "[]"


def test_find_transactions_by_phone_invalid_data() -> None:
    """Проверка устойчивости к некорректным типам данных в описании."""
    transactions: List[Dict[str, Any]] = [
        {"description": None, "amount": -100},
        {"description": 12345, "amount": -200},
        {"description": ["+79991112233"], "amount": -300}
    ]

    result_json = find_transactions_by_phone(transactions)
    result = json.loads(result_json)

    # Ни одна из этих транзакций не должна быть найдена (так как это не строки)
    assert len(result) == 0


def test_find_transactions_by_phone_result_structure() -> None:
    """Проверка, что возвращаемый JSON содержит все необходимые поля."""
    transactions = [
        {"date": "2024-05-20", "amount": -500, "category": "Еда", "description": "+79001112233"}
    ]

    result_json = find_transactions_by_phone(transactions)
    result = json.loads(result_json)

    assert result[0]["date"] == "2024-05-20"
    assert result[0]["amount"] == -500
    assert result[0]["description"] == "+79001112233"


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"description": "МТС +79991112233", "amount": -100},
        {"description": "Без номера", "amount": -200},
    ]


def test_with_fixture(sample_transactions: List[Dict[str, Any]]) -> None:
    result = json.loads(find_transactions_by_phone(sample_transactions))
    assert len(result) == 1
