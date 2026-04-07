from datetime import datetime

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    data = [
        {
            "Дата операции": "2023-09-15",
            "Сумма операции": 1000.0,
            "Категория": "Супермаркеты",
            "Описание": "Покупка продуктов",
        },
        {
            "Дата операции": "2023-07-10",
            "Сумма операции": 800.0,
            "Категория": "Супермаркеты",
            "Описание": "Еженедельная закупка",
        },
        {
            "Дата операции": "2023-06-05",
            "Сумма операции": 600.0,
            "Категория": "Супермаркеты",
            "Описание": "Большая закупка",
        },
        {"Дата операции": "2023-08-20", "Сумма операции": 300.0, "Категория": "Развлечения", "Описание": "Кинотеатр"},
        {
            "Дата операции": "2023-09-01",
            "Сумма операции": 500.0,
            "Категория": "Супермаркеты",
            "Описание": "Хлеб и молоко",
        },
        {"Дата операции": "2023-09-25", "Сумма операции": 200.0, "Категория": "Кафе", "Описание": "Кофе с другом"},
    ]
    return pd.DataFrame(data)


def test_spending_by_category_specific_date(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_category(sample_transactions, category="Супермаркеты", date="2023-10-01")
    assert len(result) == 3
    assert all(result["Категория"] == "Супермаркеты")
    # Проверяем, что транзакция старше 3 месяцев не попала
    assert "2023-06-05" not in result["Дата операции"].values


def test_spending_by_category_current_date(sample_transactions: pd.DataFrame) -> None:
    # Передаём дату явно вместо использования datetime.now()
    result = spending_by_category(sample_transactions, category="Кафе", date="2023-10-01")  # Явно указываем дату

    # Проверяем, что найдена одна транзакция
    assert len(result) == 1
    # Проверяем сумму
    assert result.iloc[0]["Сумма операции"] == 200.0
    # Проверяем описание
    assert result.iloc[0]["Описание"] == "Кофе с другом"
    # Дополнительно проверяем дату транзакции
    transaction_date = result.iloc[0]["Дата операции"]
    expected_date = datetime(2023, 9, 25)
    assert transaction_date.date() == expected_date.date()


def test_spending_by_category_boundary_dates(sample_transactions: pd.DataFrame) -> None:
    # Создаём дату ровно 3 месяца назад от 2023-10-01 → 2023-07-01
    three_months_ago = datetime(2023, 7, 1)
    transactions_copy = sample_transactions.copy()

    # Добавляем транзакцию с корректной датой (datetime)
    new_transaction = pd.DataFrame(
        [
            {
                "Дата операции": three_months_ago,
                "Сумма операции": 100.0,
                "Категория": "Супермаркеты",
                "Описание": "Ровно 3 месяца назад",
            }
        ]
    )

    # Объединяем с существующими транзакциями
    transactions_with_boundary = pd.concat([transactions_copy, new_transaction], ignore_index=True)

    result = spending_by_category(transactions_with_boundary, "Супермаркеты", "2023-10-01")

    # Отладочная печать: смотрим все описания и даты в результате
    print("Все описания в результате:", result["Описание"].tolist())
    print("Все даты в результате:", [d.date() for d in result["Дата операции"]])

    # Проверяем, что транзакция с описанием попала в результат
    assert any(result["Описание"] == "Ровно 3 месяца назад"), (
        f"Транзакция 'Ровно 3 месяца назад' не найдена в результате. " f"Найдено: {result['Описание'].tolist()}"
    )

    # Дополнительно проверяем дату транзакции
    boundary_transaction = result[result["Описание"] == "Ровно 3 месяца назад"]
    assert boundary_transaction["Дата операции"].iloc[0].date() == three_months_ago.date(), (
        f"Дата транзакции не совпадает: ожидаем {three_months_ago.date()}, "
        f"получили {boundary_transaction['Дата операции'].iloc[0].date()}"
    )
