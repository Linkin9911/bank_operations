from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import load_transactions
from src.views import main_page


def main() -> None:
    # Загрузка данных
    transactions = load_transactions("data/operations.xlsx")

    # 1. Главная страница
    print("=== ГЛАВНАЯ СТРАНИЦА ===")
    result = main_page("2023-10-15 14:30:00")
    print(result)
    print()

    # 2. Инвесткопилка: расчёт сбережений за октябрь 2023 с округлением до 50 руб.
    print("=== ИНВЕСТКОПИЛКА ===")
    savings = investment_bank("2023-10", transactions.to_dict("records"), 50)
    print(f"Сумма для инвесткопилки: {savings} руб.")
    print()

    # 3. Отчёт «Траты по категории»: траты на «Супермаркеты» за последние 3 месяца
    print("=== ОТЧЁТ: ТРАТЫ ПО КАТЕГОРИИ ===")
    supermarket_spending = spending_by_category(transactions, category="Супермаркеты", date="2023-10-15")
    if not supermarket_spending.empty:
        print("Траты на супермаркеты за последние 3 месяца:")
        print(supermarket_spending.to_string(index=False))
    else:
        print("Нет транзакций по категории «Супермаркеты» за последние 3 месяца.")


if __name__ == "__main__":
    main()
