from datetime import datetime


def investment_bank(month: str, transactions: list, rounding_limit: int) -> float:
    try:
        # Валидация формата месяца
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        raise ValueError("Некорректный формат месяца")

    total_savings = 0.0

    for transaction in transactions:
        transaction_date = transaction["Дата операции"]
        # Проверяем, относится ли транзакция к указанному месяцу
        if transaction_date.startswith(month):
            amount = transaction["Сумма операции"]
            # Пропускаем отрицательные суммы
            if amount < 0:
                continue
            # Округление вверх до ближайшего кратного rounding_limit
            if amount % rounding_limit == 0:
                # Сумма уже кратна лимиту — сбережений нет
                savings = 0.0
            else:
                rounded_amount = ((amount // rounding_limit) + 1) * rounding_limit
                savings = rounded_amount - amount
            total_savings += savings

    return total_savings
