from datetime import datetime
from typing import Optional  # Добавляем импорт

import pandas as pd


def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None  # Явно указываем Optional[str]
) -> pd.DataFrame:
    # Если дата не указана, используем текущую
    if date is None:
        target_date = datetime.now()
    else:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Некорректный формат даты")

    # Точный расчёт даты 3 месяца назад
    target_year = target_date.year
    target_month = target_date.month

    if target_month <= 3:
        three_months_ago_year = target_year - 1
        three_months_ago_month = 12 + (target_month - 3)
    else:
        three_months_ago_year = target_year
        three_months_ago_month = target_month - 3

    three_months_ago = datetime(three_months_ago_year, three_months_ago_month, 1)

    # Преобразуем колонку 'Дата операции' в datetime для корректного сравнения
    transactions_copy = transactions.copy()
    transactions_copy["Дата операции"] = pd.to_datetime(transactions_copy["Дата операции"])

    # Фильтруем транзакции: категория и дата в пределах 3 месяцев
    filtered = transactions_copy[
        (transactions_copy["Категория"] == category)
        & (transactions_copy["Дата операции"] >= three_months_ago)
        & (transactions_copy["Дата операции"] <= target_date)
    ]

    return filtered[["Дата операции", "Сумма операции", "Описание", "Категория"]].copy()
