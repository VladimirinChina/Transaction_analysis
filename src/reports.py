from typing import List, Dict, Any


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
