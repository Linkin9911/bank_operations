import json
import sys

import pandas as pd

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import load_transactions
from src.views import main_page


def main() -> None:
    """
    Основная функция приложения.

    Загружает данные и запускает все сервисы:
    - главную страницу;
    - расчёт инвесткопилки;
    - отчёт о тратах по категории.
    """
    try:
        # 1. Загрузка транзакций из Excel‑файла
        print("=== ЗАГРУЗКА ДАННЫХ ===")
        transactions = load_transactions("data/operations.xlsx")
        print("Данные загружены успешно.")
        print()

        # 2. Главная страница
        print("=== ГЛАВНАЯ СТРАНИЦА ===")
        result = main_page("2023-10-15 14:30:00")
        print(result)
        print()

        # 3. Инвесткопилка: расчёт сбережений за октябрь 2023 с округлением до 50 руб.
        print("=== ИНВЕСТКОПИЛКА ===")
        try:
            savings = investment_bank("2023-10", transactions.to_dict("records"), 50)
            print(f"Сумма для инвесткопилки: {savings} руб.")
        except ValueError as e:
            print(f"Ошибка расчёта инвесткопилки: {e}")
            sys.exit(1)
        print()

        # 4. Отчёт «Траты по категории»: траты на «Супермаркеты» за последние 3 месяца
        print("=== ОТЧЁТ: ТРАТЫ ПО КАТЕГОРИИ ===")
        try:
            supermarket_spending_json = spending_by_category(transactions, category="Супермаркеты", date="2023-10-15")

            # Парсинг JSON
            supermarket_spending_list = json.loads(supermarket_spending_json)

            # Вывод отчёта
            if supermarket_spending_list:
                print("Траты на супермаркеты за последние 3 месяца:")
                df = pd.DataFrame(supermarket_spending_list)
                print(df.to_string(index=False))
            else:
                print("Нет транзакций по категории «Супермаркеты» за последние 3 месяца.")
        except json.JSONDecodeError as e:
            print(f"Ошибка: не удалось распарсить JSON‑отчёт. {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка при формировании отчёта: {e}")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"Ошибка загрузки файла транзакций: {e}. Проверьте путь к файлу 'data/operations.xlsx'.")
        sys.exit(1)
    except PermissionError as e:
        print(f"Ошибка доступа к файлу: {e}. У вас нет прав на чтение файла.")
        sys.exit(1)
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
