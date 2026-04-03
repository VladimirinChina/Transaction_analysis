from datetime import datetime, timedelta


def filter_by_period(operations, date_str: str, period: str = "M"):
    target_date = datetime.strptime(date_str, "%d.%m.%Y")

    if period == "M":
        start = target_date.replace(day=1)
    elif period == "Y":
        start = target_date.replace(month=1, day=1)
    elif period == "W":
        start = target_date - timedelta(days=target_date.weekday())
    elif period == "ALL":
        start = min(op["date"] for op in operations)
    else:
        raise ValueError("Invalid period")

    return [
        op for op in operations
        if start <= op["date"] <= target_date
    ]
