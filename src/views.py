import json
import logging
from typing import Any, Dict, cast

from src.reports import get_expenses_summary, get_income_summary
from src.utils import (
    filter_by_period,
    get_currency_rates,
    get_stock_prices,
    read_operations,
)

# Настройка логирования для отслеживания ошибок в консоли
logger = logging.getLogger(__name__)


def load_user_settings() -> Dict[str, Any]:
    """Загружает пользовательские настройки из JSON файла."""
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            data = cast(Dict[str, Any], json.load(f))
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
        # Возвращаем дефолтные настройки, чтобы программа не упала дальше
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}


def get_events_page(date_str: str, period: str = "M") -> str:
    """Формирует итоговый JSON-отчет для главной страницы."""
    try:
        # 1. Загружаем данные
        operations = read_operations("data/operations.xlsx")

        # 2. Фильтруем по периоду
        filtered = filter_by_period(operations, date_str, period)

        # 3. Собираем финансовые отчеты
        expenses = get_expenses_summary(filtered)
        income = get_income_summary(filtered)

        # 4. Загружаем настройки и получаем внешние данные (курсы, акции)
        settings = load_user_settings()

        # Получаем данные, используя ключи из настроек
        currencies = settings.get("user_currencies", [])
        stocks = settings.get("user_stocks", [])

        currency_rates = get_currency_rates(currencies)
        stock_prices = get_stock_prices(stocks)

        # 5. Собираем итоговый результат
        result = {
            "expenses": expenses,
            "income": income,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }

        # Возвращаем красивый JSON
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Критическая ошибка при формировании страницы: {e}")
        return json.dumps({"error": "Internal server error"}, ensure_ascii=False)
