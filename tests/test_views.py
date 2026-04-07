from unittest.mock import MagicMock
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import main_page


@pytest.fixture
def mock_transactions() -> pd.DataFrame:  # Добавляем аннотацию возвращаемого типа
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
def test_main_page(
    mock_load: MagicMock, mock_transactions: pd.DataFrame  # Аннотируем тип mock  # Аннотируем тип фикстуры
) -> None:  # Указываем, что функция не возвращает значение
    mock_load.return_value = mock_transactions
    result = main_page("2023-10-01 12:00:00")

    assert result["greeting"] == "Добрый день"
    assert len(result["cards"]) == 2  # Теперь пройдёт: 2 уникальные карты

    card_digits = [card["last_digits"] for card in result["cards"]]
    assert "5814" in card_digits
    assert "7512" in card_digits

    assert len(result["top_transactions"]) == 5
    # Проверка сортировки
    dates = [t["Дата операции"] for t in result["top_transactions"]]
    assert dates == sorted(dates, reverse=True)
