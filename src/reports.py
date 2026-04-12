import re
from typing import Optional

import pandas as pd


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """
    Формирует отчёт по тратам по категории за последние 3 месяца.

    Args:
        transactions (pd.DataFrame): DataFrame с транзакциями. Должен содержать колонки:
            - 'Дата операции' (в формате YYYY-MM-DD или преобразуемом в datetime)
            - 'Сумма операции'
            - 'Категория'
            - 'Описание'
        category (str): Категория для фильтрации.
        date (Optional[str], optional): Дата для расчёта периода (YYYY-MM-DD).
            Если None — используется текущая дата. По умолчанию None.

    Returns:
        str: JSON‑строка с отфильтрованными транзакциями в формате:
            [
                {
                    'Дата операции': 'YYYY-MM-DD',
            'Сумма операции': float,
            'Категория': str,
            'Описание': str
                }
                ...
            ]

    Raises:
        ValueError: Если дата имеет некорректный формат или если в колонке 'Дата операции'
            содержатся данные, которые невозможно преобразовать в datetime.
        KeyError: Если в DataFrame отсутствуют необходимые колонки.

        Example:
        >>> # Создаём тестовый DataFrame
        >>> data = {
        ...     'Дата операции': ['2023-09-01', '2023-09-15', '2023-10-01'],
        ...     'Сумма операции': [1262.0, 899.5, 2500.0],
        ...     'Категория': ['Супермаркеты', 'Супермаркеты', 'Развлечения'],
        ...     'Описание': ['Покупка продуктов', 'Продукты', 'Кинотеатр']
        ... }
        >>> df = pd.DataFrame(data)
        >>>
        >>> result = spending_by_category(df, "Супермаркеты", "2023-10-15")
        >>> print(result)
        '[
          {"Дата операции": "2023-09-01", "Сумма операции": 1262.0,
          "Категория": "Супермаркеты", "Описание": "Покупка продуктов"},
          {"Дата операции": "2023-09-15", "Сумма операции": 899.5,
          "Категория": "Супермаркеты", "Описание": "Продукты"}
        ]'
    """
    # Проверяем наличие необходимых колонок
    required_columns = ["Дата операции", "Сумма операции", "Категория", "Описание"]
    missing_columns = [col for col in required_columns if col not in transactions.columns]
    if missing_columns:
        raise KeyError(f"Отсутствуют необходимые колонки: {missing_columns}")

    # Преобразуем столбец с датами в datetime, если ещё не сделано
    if transactions["Дата операции"].dtype != "datetime64[ns]":
        try:
            transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])
        except (ValueError, pd.errors.ParserError) as e:
            raise ValueError(f"Некорректный формат даты в колонке 'Дата операции': {e}")

    # Обрабатываем параметр date
    if date is not None:
        try:
            # Явная проверка формата YYYY-MM-DD
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
                raise ValueError("Некорректный формат даты")
            target_date = pd.to_datetime(date)
        except ValueError, pd.errors.ParserError:
            raise ValueError("Некорректный формат даты")
    else:
        target_date = pd.Timestamp.now()

    # Рассчитываем дату начала периода (3 месяца назад)
    start_date = target_date - pd.DateOffset(months=3)

    # Фильтруем транзакции по категории и периоду
    result_data = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= target_date)
    ].copy()

    # Если нет данных, возвращаем пустой JSON-массив
    if result_data.empty:
        return "[]"

    # Форматируем даты обратно в строку
    result_data["Дата операции"] = result_data["Дата операции"].dt.strftime("%Y-%m-%d")

    # Конвертируем в JSON и явно приводим к строке
    result_json = str(result_data.to_json(orient="records", force_ascii=False))
    return result_json
