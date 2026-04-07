from typing import Any
from typing import Dict
from typing import List

import pytest

from src.services import investment_bank


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми транзакциями для инвесткопилки."""
    return [
        {"Дата операции": "2023-10-01", "Сумма операции": 1712.0},
        {"Дата операции": "2023-10-02", "Сумма операции": 850.0},
        {"Дата операции": "2023-10-03", "Сумма операции": 245.0},
        {"Дата операции": "2023-09-25", "Сумма операции": 999.0},  # другой месяц
        {"Дата операции": "2023-10-04", "Сумма операции": 50.0},
    ]


def test_investment_bank_round_to_50(sample_transactions: List[Dict[str, Any]]) -> None:
    result = investment_bank("2023-10", sample_transactions, 50)
    # Расчёт: 1712 → 1750 (38), 850 → 850 (0), 245 → 250 (5), 50 → 50 (0)
    assert result == 43.0


def test_investment_bank_exact_multiples() -> None:
    transactions: List[Dict[str, Any]] = [
        {"Дата операции": "2023-10-05", "Сумма операции": 100.0},
        {"Дата операции": "2023-10-06", "Сумма операции": 200.0},
        {"Дата операции": "2023-10-07", "Сумма операции": 300.0},
    ]
    result = investment_bank("2023-10", transactions, 100)
    assert result == 0.0  # Все суммы уже кратны 100 — сбережений нет


def test_investment_bank_negative_amounts() -> None:
    transactions: List[Dict[str, Any]] = [
        {"Дата операции": "2023-10-08", "Сумма операции": -500.0},
        {"Дата операции": "2023-10-09", "Сумма операции": -245.0},
    ]
    result = investment_bank("2023-10", transactions, 50)
    assert result == 0.0  # Отрицательные суммы игнорируются


def test_investment_bank_invalid_month_format() -> None:
    transactions: List[Dict[str, Any]] = [{"Дата операции": "2023-10-01", "Сумма операции": 100.0}]
    with pytest.raises(ValueError, match="Некорректный формат месяца"):
        investment_bank("invalid-month", transactions, 50)
