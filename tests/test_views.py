from unittest.mock import MagicMock
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import main_page


@pytest.fixture
def mock_transactions() -> pd.DataFrame:
    """
    Фикстура с тестовыми транзакциями для проверки главной страницы.

    Содержит транзакции разных категорий и сумм для тестирования отображения данных.

    Returns:
        pd.DataFrame: DataFrame с тестовыми транзакциями, включающий колонки:
            - 'Номер карты' (int): номер банковской карты;
            - 'Сумма операции' (float): сумма транзакции;
            - 'Категория' (str): категория транзакции;
            - 'Описание' (str): описание транзакции;
            - 'Дата операции' (str): дата в формате 'YYYY‑MM‑DD'.
    """
    return pd.DataFrame(
        {
            "Номер карты": [1234567890125814, 1234567890127512, 1234567890125814, 1234567890127512, 1234567890125814],
            "Сумма операции": [1262.00, 7.94, 500.00, 200.00, 1000.00],
            "Категория": ["Переводы", "Супермаркеты", "Развлечения", "Кафе", "Переводы"],
            "Описание": ["Перевод", "Покупка в магазине", "Кино", "Кофе", "Перевод другу"],
            "Дата операции": ["2023-09-30", "2023-09-29", "2023-09-28", "2023-09-27", "2023-09-26"],
        }
    )


@patch("src.views.load_transactions")
def test_main_page(mock_load_transactions: MagicMock, mock_transactions: pd.DataFrame) -> None:
    """
    Тест главной страницы приложения.

    Проверяет, что функция `main_page` корректно обрабатывает данные и возвращает
    непустую строку с информацией о транзакциях.

    Args:
        mock_load_transactions (MagicMock): Mock‑объект для функции `load_transactions`,
            подменяющий реальную загрузку данных на тестовые транзакции.
        mock_transactions (pd.DataFrame): Фиктивные данные транзакций,
            предоставляемые фикстурой `mock_transactions`.

    Process:
        1. Подменяет реальную функцию загрузки данных на фиктивные транзакции.
        2. Вызывает функцию `main_page` с тестовой датой и временем.
        3. Проверяет, что результат:
            - является строкой;
            - не пуст;
            - содержит упоминания ключевых категорий транзакций.

    Example:
        >>> test_main_page(...)
        # Тест проходит, если все assert‑проверки успешны

    Raises:
        AssertionError: Если какой‑либо из assert‑проверков не пройден.
    """
    mock_load_transactions.return_value = mock_transactions
    # Передаём полную дату и время в ожидаемом формате
    result = main_page(date_input="2023-09-01 12:00:00")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Переводы" in result
    assert "Супермаркеты" in result
