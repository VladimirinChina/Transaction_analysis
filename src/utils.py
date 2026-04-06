from datetime import datetime, timedelta
from typing import List, Dict, Any, cast

import pandas as pd


def read_operations(file_path: str) -> List[Dict[str, Any]]:
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
