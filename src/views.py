import json

from src.utils import get_currency_rates
from src.utils import get_greeting
from src.utils import get_stock_prices
from src.utils import load_transactions


def main_page(date_input: str) -> dict:
    """
    Главная функция для страницы «Главная».

    Args:
        date_input (str): Дата в формате YYYY-MM-DD HH:MM:SS.

    Returns:
        dict: JSON-ответ с данными для страницы.
    """
    # Загрузка данных
    transactions = load_transactions("data/operations.xlsx")

    # Приветствие
    greeting = get_greeting(date_input)

    # Обработка транзакций по картам с корректной агрегацией
    card_groups = transactions.groupby("Номер карты")
    cards_data = []
    for card_number, group in card_groups:
        total_spent = abs(group["Сумма операции"]).sum()  # модуль суммы
        cashback = total_spent * 0.01
        cards_data.append(
            {
                "last_digits": str(card_number)[-4:],
                "total_spent": round(total_spent, 2),
                "cashback": round(cashback, 2),
            }
        )

    # Сортировка транзакций по дате (новые первыми) и выбор топ‑5
    transactions_sorted = transactions.sort_values(by="Дата операции", ascending=False)
    top_transactions = transactions_sorted.head(5)[
        ["Дата операции", "Сумма операции", "Категория", "Описание"]
    ].to_dict(orient="records")

    # Курсы валют и акции
    with open("user_settings.json", "r") as f:
        settings = json.load(f)
    currency_rates = get_currency_rates(settings["user_currencies"])
    stock_prices = get_stock_prices(settings["user_stocks"])

    return {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
