import json
import logging
import os

import pandas as pd
from datetime import datetime, timedelta
from functools import wraps
from typing import List, Dict, Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)
RT = TypeVar("RT")

DATA_DIR = "data"


def report_to_file(filename: Optional[str] = None) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> RT:
            result = func(*args, **kwargs)

            os.makedirs(DATA_DIR, exist_ok=True)

            file_name = filename or f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_name = os.path.join(DATA_DIR, file_name)

            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False))
                logger.info(f"Отчет сохранен в файл: {file_name}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")

            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None
) -> str:
    logger.info("Расчет расходов по категориям '%s'" % category)

    #  копия, чтобы не менять оригинальный DataFrame и избежать предупреждений
    df = transactions.copy()

    if date:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    # Приводим к формату datetime
    df["date"] = pd.to_datetime(df["date"])

    filtered = df[
        (df["category"] == category)
        & (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["amount"] < 0)
    ]

    result = {
        "category": category,
        "total_spent": int(abs(filtered["amount"].sum())),
        "transactions_count": int(len(filtered)),
    }

    return json.dumps(result, ensure_ascii=False)


def get_expenses_summary(operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    # только траты
    expenses = [op for op in operations if op.get("amount", 0) < 0]

    total_amount = int(abs(sum(op.get("amount", 0) for op in expenses)))

    category_sums: Dict[str, float] = {}

    for op in expenses:
        category = op.get("category", "Без категории")
        amount = abs(op.get("amount", 0))

        if category not in category_sums:
            category_sums[category] = 0

        category_sums[category] += amount

    # отдельно "Наличные" и "Переводы"
    transfers_and_cash = []

    for special in ["Наличные", "Переводы"]:
        if special in category_sums:
            transfers_and_cash.append({
                "category": special,
                "amount": int(category_sums.pop(special))
            })

    # сортировка категорий
    sorted_categories = sorted(
        category_sums.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # топ-7
    top_categories = sorted_categories[:7]
    other_categories = sorted_categories[7:]

    main = [
        {"category": cat, "amount": int(amount)}
        for cat, amount in top_categories
    ]

    # добавляем "Остальное"
    if other_categories:
        other_sum = sum(amount for _, amount in other_categories)
        main.append({
            "category": "Остальное",
            "amount": int(other_sum)
        })

    return {
        "total_amount": total_amount,
        "main": main,
        "transfers_and_cash": sorted(
            transfers_and_cash,
            key=lambda x: x["amount"],
            reverse=True
        )
    }


def get_income_summary(operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    income = [op for op in operations if op.get("amount", 0) > 0]

    total_amount = int(sum(op.get("amount", 0) for op in income))

    category_sums: Dict[str, float] = {}

    for op in income:
        category = op.get("category", "Без категории")
        amount = op.get("amount", 0)

        if category not in category_sums:
            category_sums[category] = 0

        category_sums[category] += amount

    sorted_categories = sorted(
        category_sums.items(),
        key=lambda x: x[1],
        reverse=True
    )

    main = [
        {"category": cat, "amount": int(amount)}
        for cat, amount in sorted_categories
    ]

    return {
        "total_amount": total_amount,
        "main": main
    }
