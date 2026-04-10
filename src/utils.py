import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, cast

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

if not EXCHANGE_API_KEY:
    raise ValueError("EXCHANGE_API_KEY not set")


def read_operations(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает транзакции из Excel-файла и приводит их к стандартному формату.

    Функция:
    - переименовывает столбцы в удобные имена,
    - оставляет только нужные поля,
    - преобразует колонку 'date' в datetime,
    - заменяет пропущенные значения на пустые строки.
    :param file_path: Путь к Excel-файлу.
    :return: Список транзакций в виде словарей.
    """
    df = pd.read_excel(file_path)

    # приводим названия к удобным
    df = df.rename(columns={
        "Дата операции": "date",
        "Номер карты": "card",
        "Сумма операции с округлением": "amount",
        "Категория": "category",
        "Описание": "description",
    })

    # оставляем только нужное
    df = df[["date", "card", "amount", "category", "description"]]

    # приводим дату
    df["date"] = pd.to_datetime(df["date"])

    # убираем NaN
    df = df.fillna("")

    return cast(List[Dict[str, Any]], df.to_dict(orient="records"))


def filter_by_period(
        operations: List[Dict[str, Any]],
        date_str: str,
        period: str = "M"
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по заданному периоду.

    Поддерживаемые периоды:
        - "M" — месяц
        - "Y" — год
        - "W" — неделя
        - "ALL" — все доступные данные
    :param operations: Список транзакций.
    :param date_str: Целевая дата в формате 'DD.MM.YYYY'.
    :param period: Тип периода.
    :return: Отфильтрованный список транзакций.

    :raises ValueError: Если передан неподдерживаемый период.
    """
    target_date = datetime.strptime(date_str, "%d.%m.%Y")

    if period == "M":
        start = target_date.replace(day=1)
    elif period == "Y":
        start = target_date.replace(month=1, day=1)
    elif period == "W":
        start = target_date - timedelta(days=target_date.weekday())
    elif period == "ALL":
        start = min(op["date"] for op in operations) if operations else target_date
    else:
        raise ValueError("Invalid period")

    return [
        op for op in operations
        if start <= op["date"] <= target_date
    ]


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Получает текущие курсы валют относительно рубля.

    Функция отправляет запрос к внешнему API и возвращает
    курсы только для указанных валют.
    :param currencies: Список кодов валют (например, ["USD", "EUR"]).
    :return: Список словарей со структурой:
        - currency: код валюты
        - rate: курс
    """
    response = requests.get("https://api.exchangerate-api.com/v4/latest/RUB")
    data = response.json()

    result = []
    for currency in currencies:
        rate = data["rates"].get(currency)
        if rate:
            result.append({
                "currency": currency,
                "rate": round(rate, 2)
            })
    return result


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает текущие цены акций через API Alpha Vantage.

    Для работы требуется наличие переменной окружения EXCHANGE_API_KEY.
    :param stocks: Список тикеров акций (например, ["AAPL", "TSLA"]).
    :return: Список словарей со структурой:
        - stock: тикер
        - price: цена акции
    """
    result = []

    for stock in stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={EXCHANGE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        price = data.get("Global Quote", {}).get("05. price")
        if price:
            result.append({
                "stock": stock,
                "price": round(float(price), 2)
            })

    return result
