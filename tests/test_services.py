import json
from typing import Any
from typing import Dict
from typing import List

import pytest

from src.services import investment_bank


@pytest.fixture
def sample_investment_transactions() -> List[Dict[str, Any]]:
    """
    Фикстура с тестовыми транзакциями для инвестиционного банка.

    Предоставляет набор транзакций за разные месяцы для тестирования расчёта сбережений.

    Returns:
        List[Dict[str, Any]]: Список словарей с транзакциями, каждый содержит:
            - 'Дата операции' (str): дата в формате 'YYYY‑MM‑DD';
            - 'Сумма операции' (float): сумма транзакции.
    """
    return [
        {"Дата операции": "2023-10-05", "Сумма операции": 143.0},
        {"Дата операции": "2023-10-10", "Сумма операции": 188.0},
        {"Дата операции": "2023-09-15", "Сумма операции": 51.0},
        {"Дата операции": "2023-10-20", "Сумма операции": 75.0},
    ]


@pytest.mark.parametrize(
    "month,rounding_limit,expected_savings",
    [
        ("2023-10", 50, 106.0),  # 143→100 (43), 188→150 (38), 75→50 (25) → 43+38+25=106
        ("2023-09", 50, 1.0),  # 51→50 (1)
    ],
)
def test_investment_bank_parametrized(
    sample_investment_transactions: List[Dict[str, Any]], month: str, rounding_limit: int, expected_savings: float
) -> None:
    """
    Параметризованный тест для проверки расчёта сбережений в инвестиционном банке.

    Проверяет корректность расчёта суммы для инвесткопилки при разных параметрах.

    Args:
        sample_investment_transactions (List[Dict[str, Any]]): Фиктивные транзакции
            для тестирования.
        month (str): Месяц для расчёта в формате 'YYYY‑MM'.
        rounding_limit (int): Лимит округления (целое число).
        expected_savings (float): Ожидаемая сумма сбережений для проверки.
    """
    result_json = investment_bank(month, sample_investment_transactions, rounding_limit)
    result = json.loads(result_json)
    assert result["investment_savings"] == pytest.approx(expected_savings, rel=1e-2)


def test_investment_bank_exact_multiples(sample_investment_transactions: List[Dict[str, Any]]) -> None:
    """
    Тест для сумм, кратных лимиту округления.

    Проверяет, что если все суммы кратны лимиту округления, сбережения равны 0.

    Args:
        sample_investment_transactions (List[Dict[str, Any]]): Фиктивные транзакции
            (не используются в тесте, но требуются для сигнатуры).
    """
    # Транзакции с суммами, кратными 50
    exact_transactions: List[Dict[str, Any]] = [
        {"Дата операции": "2023-10-01", "Сумма операции": 100.0},
        {"Дата операции": "2023-10-02", "Сумма операции": 150.0},
    ]
    result_json = investment_bank("2023-10", exact_transactions, 50)
    result = json.loads(result_json)
    assert result["investment_savings"] == 0.0


def test_investment_bank_negative_amounts(sample_investment_transactions: List[Dict[str, Any]]) -> None:
    """
    Тест с отрицательными суммами транзакций.

    Проверяет обработку отрицательных сумм — ожидаем, что сбережения неотрицательны.

    Args:
        sample_investment_transactions (List[Dict[str, Any]]): Фиктивные транзакции
            (не используются в тесте, но требуются для сигнатуры).
    """
    negative_transactions: List[Dict[str, Any]] = [
        {"Дата операции": "2023-10-01", "Сумма операции": -100.0},
        {"Дата операции": "2023-10-02", "Сумма операции": -50.0},
    ]
    result_json = investment_bank("2023-10", negative_transactions, 50)
    result = json.loads(result_json)
    # Предполагаем, что отрицательные суммы игнорируются или обрабатываются особым образом
    assert result["investment_savings"] >= 0.0


def test_investment_bank_invalid_month_format() -> None:
    """
    Тест некорректного формата месяца.

    Проверяет, что функция корректно выбрасывает ValueError при неверном формате месяца.
    """
    transactions: List[Dict[str, Any]] = [{"Дата операции": "2023-10-01", "Сумма операции": 100.0}]
    with pytest.raises(ValueError, match="Некорректный формат месяца"):
        investment_bank("invalid-month", transactions, 50)


@pytest.mark.parametrize(
    "month,expected_savings", [("2023-10", 0.0), ("2023-11", 0.0)]  # Пустой список транзакций  # Месяц без транзакций
)
def test_investment_bank_complex_scenarios(month: str, expected_savings: float) -> None:
    """
    Сложные сценарии: пустые данные, месяц без транзакций.

    Проверяет поведение функции при крайних случаях:
    - пустой список транзакций;
    - месяц, для которого нет транзакций.

    Args:
        month (str): Месяц для расчёта в формате 'YYYY‑MM'.
        expected_savings (float): Ожидаемая сумма сбережений (должна быть 0.0).
    """
    empty_transactions: List[Dict[str, Any]] = []
    result_json = investment_bank(month, empty_transactions, 50)
    result = json.loads(result_json)
    assert result["investment_savings"] == expected_savings
