from src.utils import filter_by_period
from datetime import datetime


def test_filter_by_month():
    data = [
        {"date": datetime(2024, 5, 1)},
        {"date": datetime(2024, 5, 20)},
        {"date": datetime(2024, 4, 30)},
    ]

    result = filter_by_period(data, "20.05.2024", "M")

    assert len(result) == 2
