import json
import logging
import re
from typing import Any, Dict, List

# Настройка логгера
logger = logging.getLogger(__name__)


def find_transactions_by_phone(transactions: List[Dict[str, Any]]) -> str:
    """
    Находит транзакции, содержащие номера телефонов в описании.

    :param transactions: Список словарей с данными о транзакциях.
    :return: Строка в формате JSON с отфильтрованными транзакциями.
    """
    logger.info("Запуск поиска по номерам телефонов")

    # Регулярное выражение для поиска российских номеров в разных форматах:
    # +7 999 123-45-67, 89991234567, 7(999)123-45-67 и т.д.
    phone_pattern = re.compile(
        r"(?:^|(?<=\s))(?:\+7|8|7)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?=$|[\s.,])")

    result: List[Dict[str, Any]] = []

    for transaction in transactions:
        # Получаем описание, проверяя, что оно является строкой
        description = transaction.get("description")

        if isinstance(description, str):
            if phone_pattern.search(description):
                logger.debug(f"Найден номер в транзакции: {description}")
                result.append(transaction)
        else:
            # Если описание отсутствует или это не строка, просто пропускаем
            continue

    logger.info(f"Найдено транзакций с номерами: {len(result)}")

    # Возвращаем результат в формате JSON с поддержкой кириллицы
    return json.dumps(result, ensure_ascii=False)
