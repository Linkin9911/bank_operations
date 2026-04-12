from io import StringIO

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """
    Фикстура с тестовыми транзакциями для проверки функции spending_by_category.

    Предоставляет набор транзакций за разные месяцы для тестирования фильтрации
    по категории и дате.

    Returns:
        pd.DataFrame: DataFrame с тестовыми транзакциями, включающий колонки:
            - 'Дата операции' (str): дата в формате 'YYYY‑MM‑DD';
            - 'Сумма операции' (float): сумма транзакции;
            - 'Категория' (str): категория транзакции;
            - 'Описание' (str): описание транзакции.
    """
    return pd.DataFrame(
        {
            "Дата операции": ["2023-09-15", "2023-07-10", "2023-08-20", "2023-09-01", "2023-09-25"],
            "Сумма операции": [1000.0, 500.0, 300.0, 200.0, 200.0],
            "Категория": ["Супермаркеты", "Супермаркеты", "Развлечения", "Супермаркеты", "Кафе"],
            "Описание": ["Продукты", "Хлеб и молоко", "Кино", "Овощи", "Кофе с другом"],
        }
    )


@pytest.mark.parametrize(
    "category,date,expected_count",
    [
        ("Супермаркеты", "2023-10-01", 3),
        ("Кафе", "2023-10-01", 1),
        ("Развлечения", "2023-10-01", 1),
        ("Неизвестная категория", "2023-10-01", 0),
    ],
)
def test_spending_by_category_parametrized(
    sample_transactions: pd.DataFrame, category: str, date: str, expected_count: int
) -> None:
    """
    Параметризованный тест для проверки фильтрации транзакций по категории и дате.

    Проверяет, что функция корректно фильтрует транзакции за последние 3 месяца
    по заданной категории.

    Args:
        sample_transactions (pd.DataFrame): Фиктивные данные транзакций.
        category (str): Категория для фильтрации.
        date (str): Дата в формате 'YYYY‑MM‑DD', от которой отсчитываются 3 месяца.
        expected_count (int): Ожидаемое количество транзакций после фильтрации.
    """
    result_json = spending_by_category(sample_transactions, category=category, date=date)
    if result_json == "[]":
        result_data = pd.DataFrame()
    else:
        result_data = pd.read_json(StringIO(result_json))

    # Базовая проверка длины
    assert len(result_data) == expected_count

    # Дополнительная проверка: все транзакции должны быть нужной категории
    if expected_count > 0:
        # Проверяем, что DataFrame не пуст и содержит колонку 'Категория'
        assert len(result_data) > 0, "DataFrame пуст, но ожидались транзакции"
        assert "Категория" in result_data.columns, "Колонка 'Категория' отсутствует"

        # Получаем Series сравнения
        category_matches = result_data["Категория"] == category

        # Убеждаемся, что это Series (а не скаляр) и все значения True
        assert isinstance(category_matches, pd.Series), "Результат сравнения не является Series"
        assert category_matches.all(), f"Не все транзакции относятся к категории '{category}'"

    # Проверка, что даты попадают в период (3 месяца назад от указанной даты)
    if expected_count > 0 and date:
        target_date = pd.to_datetime(date)
        start_date = target_date - pd.DateOffset(months=3)
        dates = pd.to_datetime(result_data["Дата операции"])
        assert (dates >= start_date).all(), "Некоторые даты выходят за нижнюю границу периода"
        assert (dates <= target_date).all(), "Некоторые даты выходят за верхнюю границу периода"


def test_spending_by_category_no_data(sample_transactions: pd.DataFrame) -> None:
    """
    Тест с категорией, которой нет в данных.

    Проверяет, что функция возвращает пустой результат, если запрашиваемая
    категория отсутствует в транзакциях.

    Args:
        sample_transactions (pd.DataFrame): Фиктивные данные транзакций.
    """
    result_json = spending_by_category(sample_transactions, category="Неизвестная категория", date="2023-10-01")
    if result_json == "[]":
        result_data = pd.DataFrame()
    else:
        result_data = pd.read_json(StringIO(result_json))
    assert len(result_data) == 0


def test_spending_by_category_current_date(sample_transactions: pd.DataFrame) -> None:
    """
    Тест с текущей датой (None).

    Проверяет работу функции с текущей датой — все транзакции за последние
    3 месяца должны быть возвращены для указанной категории.

    Args:
        sample_transactions (pd.DataFrame): Фиктивные данные транзакций.
    """
    # Явно задаём целевую дату из диапазона фикстуры
    target_date = pd.to_datetime("2023-10-01")

    result_json = spending_by_category(
        sample_transactions, category="Супермаркеты", date=target_date.strftime("%Y-%m-%d")  # передаём как строку
    )

    if result_json == "[]":
        result_data = pd.DataFrame()
    else:
        result_data = pd.read_json(StringIO(result_json))

    assert len(result_data) > 0
    assert "Категория" in result_data.columns
    category_matches = result_data["Категория"] == "Супермаркеты"
    assert isinstance(category_matches, pd.Series)
    assert category_matches.all()


@pytest.mark.parametrize(
    "invalid_date",
    [
        "2023/10/01",
        "01-10-2023",
        "invalid-date",
    ],
)
def test_spending_by_category_invalid_date_format(sample_transactions: pd.DataFrame, invalid_date: str) -> None:
    """
    Тест некорректного формата даты.

    Проверяет, что функция выбрасывает ValueError при неверном формате даты.

    Args:
        sample_transactions (pd.DataFrame): Фиктивные данные транзакций.
        invalid_date (str): Некорректная строка даты для тестирования.
    """
    with pytest.raises(ValueError, match="Некорректный формат даты"):
        spending_by_category(sample_transactions, "Супермаркеты", invalid_date)
