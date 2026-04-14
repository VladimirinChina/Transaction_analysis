import pandas as pd

from src.reports import spending_by_category
from src.services import find_transactions_by_phone
from src.utils import filter_by_period, read_operations
from src.views import get_events_page


def main() -> None:
    # 1. Чтение данных
    operations = read_operations("data/operations.xlsx")

    # 2. Фильтрация
    filtered_operations = filter_by_period(operations, "20.05.2024", "M")

    print("=== EVENTS PAGE ===")
    print(get_events_page("20.05.2024"))

    print("\n=== PHONE SEARCH (FILTERED) ===")
    print(find_transactions_by_phone(filtered_operations))

    print("\n=== SPENDING REPORT (FILTERED) ===")
    df = pd.DataFrame(filtered_operations)
    print(spending_by_category(df, "Еда", "2024-05-20"))


if __name__ == "__main__":
    main()
