from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import get_currency_rates
from src.utils import get_greeting
from src.utils import get_stock_prices
from src.utils import load_transactions
from src.utils import logger


def test_load_transactions_success() -> None:
    """Тест успешной загрузки транзакций из Excel‑файла."""
    mock_df = pd.DataFrame({"test": [1, 2, 3]})
    with patch("pandas.read_excel", return_value=mock_df) as mock_read:
        result = load_transactions("test.xlsx")
        mock_read.assert_called_once_with("test.xlsx")
        assert isinstance(result, pd.DataFrame)
        assert result.equals(mock_df)


def test_load_transactions_file_not_found() -> None:
    """Тест обработки ошибки «файл не найден»."""
    with (
        patch("pandas.read_excel", side_effect=FileNotFoundError("Файл не найден")),
        patch.object(logger, "error") as mock_logger,
    ):
        with pytest.raises(FileNotFoundError):
            load_transactions("nonexistent.xlsx")
        mock_logger.assert_called_once()
        # Исправляем проверку: используем полную строку из лога
        assert "Ошибка загрузки файла: Файл не найден" in str(mock_logger.call_args)


def test_load_transactions_permission_error() -> None:
    """Тест обработки ошибки прав доступа."""
    with (
        patch("pandas.read_excel", side_effect=PermissionError("Нет доступа")),
        patch.object(logger, "error") as mock_logger,  # Исправлен доступ к logger
    ):
        with pytest.raises(PermissionError):
            load_transactions("restricted.xlsx")
        mock_logger.assert_called_once()


def test_get_greeting_morning() -> None:
    """
    Тест приветствия для утреннего времени (5:00–11:59).

    Проверяет возврат «Доброе утро» для времени 08:30.
    """
    result = get_greeting("2023-10-15 08:30:00")
    assert result == "Доброе утро"


def test_get_greeting_afternoon() -> None:
    """
    Тест приветствия для дневного времени (12:00–16:59).

    Проверяет возврат «Добрый день» для времени 14:00.
    """
    result = get_greeting("2023-10-15 14:00:00")
    assert result == "Добрый день"


def test_get_greeting_evening() -> None:
    """
    Тест приветствия для вечернего времени (17:00–22:59).

    Проверяет возврат «Добрый вечер» для времени 19:45.
    """
    result = get_greeting("2023-10-15 19:45:00")
    assert result == "Добрый вечер"


def test_get_greeting_night() -> None:
    """
    Тест приветствия для ночного времени (23:00–4:59).

    Проверяет возврат «Доброй ночи» для времени 02:15.
    """
    result = get_greeting("2023-10-15 02:15:00")
    assert result == "Доброй ночи"


def test_get_greeting_boundary_morning() -> None:
    """
    Тест граничных значений для утреннего приветствия.

    Проверяет переход в 5:00 (начало утра).
    """
    result = get_greeting("2023-10-15 05:00:00")
    assert result == "Доброе утро"


def test_get_greeting_boundary_night() -> None:
    """
    Тест граничного значения для ночного приветствия.

    Проверяет переход в 23:00 (начало ночи).
    """
    result = get_greeting("2023-10-15 23:00:00")
    assert result == "Доброй ночи"


def test_get_currency_rates_single_currency() -> None:
    """
    Тест получения курса для одной валюты.

    Проверяет корректность возврата данных для ['USD'].
    """
    result = get_currency_rates(["USD"])
    assert len(result) == 1
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 73.21


def test_get_currency_rates_multiple_currencies() -> None:
    """
    Тест получения курсов для нескольких валют.

    Проверяет корректность данных для ['USD', 'EUR', 'GBP'].
    """
    currencies = ["USD", "EUR", "GBP"]
    result = get_currency_rates(currencies)
    assert len(result) == 3
    usd_rate = next(item for item in result if item["currency"] == "USD")
    eur_rate = next(item for item in result if item["currency"] == "EUR")
    gbp_rate = next(item for item in result if item["currency"] == "GBP")
    assert usd_rate["rate"] == 73.21
    assert eur_rate["rate"] == 87.08
    assert gbp_rate["rate"] == 87.08  # по логике функции


def test_get_currency_rates_empty_list() -> None:
    """
    Тест обработки пустого списка валют.

    Проверяет возврат пустого списка при [] на входе.
    """
    result = get_currency_rates([])
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_stock_prices_single_stock() -> None:
    """
    Тест получения цены для одной акции.

    Проверяет корректность возврата данных для ['AAPL'].
    """
    result = get_stock_prices(["AAPL"])
    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.12


def test_get_stock_prices_multiple_stocks() -> None:
    """
    Тест получения цен для нескольких акций.

    Проверяет корректность данных для ['AAPL', 'GOOGL', 'MSFT'].
    """
    stocks = ["AAPL", "GOOGL", "MSFT"]
    result = get_stock_prices(stocks)
    assert len(result) == 3
    for stock_data in result:
        assert stock_data["stock"] in stocks
        assert stock_data["price"] == 150.12


def test_get_stock_prices_empty_list() -> None:
    """
    Тест обработки пустого списка акций.

    Проверяет возврат пустого списка при [] на входе.
    """
    result = get_stock_prices([])
    assert isinstance(result, list)
    assert len(result) == 0
