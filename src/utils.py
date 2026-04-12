import logging
from datetime import datetime

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_transactions(file_path: str) -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла.

    Args:
        file_path (str): Путь к Excel-файлу с транзакциями.

    Returns:
        pd.DataFrame: DataFrame с загруженными транзакциями.

    Raises:
        Exception: Если файл не удаётся загрузить.
    """
    try:
        df = pd.read_excel(file_path)
        logger.info("Транзакции успешно загружены")
        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
        raise


def get_greeting(current_time: str) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        current_time (str): Дата и время в формате YYYY-MM-DD HH:MM:SS.

    Returns:
        str: Приветствие («Доброе утро», «Добрый день» и т. д.).
    """
    hour = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: list) -> list:
    """
    Получает курсы валют через API (пример с фиктивными данными).

    Args:
        currencies (list): Список кодов валют (например, ['USD', 'EUR']).

    Returns:
        list: Список словарей с курсами валют.
    """
    rates = []
    for currency in currencies:
        rates.append({"currency": currency, "rate": 73.21 if currency == "USD" else 87.08})
    return rates


def get_stock_prices(stocks: list) -> list:
    """
    Получает цены акций через API.

    Args:
        stocks (list): Список тикеров акций (например, ['AAPL', 'GOOGL']).

    Returns:
        list: Список словарей с ценами акций.
    """
    prices = []
    for stock in stocks:
        prices.append({"stock": stock, "price": 150.12})
    return prices
