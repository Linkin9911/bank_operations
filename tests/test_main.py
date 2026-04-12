import json
from unittest.mock import patch

import pandas as pd
import pytest
from _pytest.capture import CaptureFixture

from src.main import main


@pytest.fixture
def mock_load_transactions() -> pd.DataFrame:
    """Фикстура для имитации загрузки транзакций."""
    return pd.DataFrame(
        {
            "Дата операции": ["2023-09-01", "2023-09-15"],
            "Сумма операции": [1262.0, 899.5],
            "Категория": ["Супермаркеты", "Супермаркеты"],
            "Описание": ["Покупка продуктов", "Продукты"],
        }
    )


def test_main_full_execution(capsys: CaptureFixture, mock_load_transactions: pd.DataFrame) -> None:
    """
    Полный тест выполнения функции main().

    Проверяет, что:
    * все модули вызываются корректно;
    * выводится ожидаемый текст в консоль;
    * нет необработанных исключений.

    Args:
        capsys: фикстура pytest для перехвата вывода в консоль.
        mock_load_transactions: фиктивные данные транзакций.
    """
    with (
        patch("src.main.load_transactions", return_value=mock_load_transactions),
        patch("src.main.main_page", return_value="Доброе утро!"),
        patch("src.main.investment_bank", return_value=150),
        patch(
            "src.main.spending_by_category",
            return_value=json.dumps(
                [
                    {
                        "Дата операции": "2023-09-01",
                        "Сумма операции": 1262.0,
                        "Категория": "Супермаркеты",
                        "Описание": "Покупка продуктов",
                    },
                    {
                        "Дата операции": "2023-09-15",
                        "Сумма операции": 899.5,
                        "Категория": "Супермаркеты",
                        "Описание": "Продукты",
                    },
                ]
            ),
        ),
    ):
        # Выполняем main()
        main()

        # Перехватываем вывод
        captured = capsys.readouterr()

        # Проверяем основные секции вывода
        assert "=== ГЛАВНАЯ СТРАНИЦА ===" in captured.out
        assert "Доброе утро!" in captured.out
        assert "=== ИНВЕСТКОПИЛКА ===" in captured.out
        assert "Сумма для инвесткопилки: 150 руб." in captured.out
        assert "=== ОТЧЁТ: ТРАТЫ ПО КАТЕГОРИИ ===" in captured.out
        assert "Траты на супермаркеты за последние 3 месяца:" in captured.out
        assert "Покупка продуктов" in captured.out
        assert "Продукты" in captured.out


def test_main_empty_transactions(capsys: CaptureFixture) -> None:
    """
    Тест main() с пустыми транзакциями.

    Проверяет обработку случая, когда load_transactions возвращает пустой DataFrame.

    Args:
        capsys: фикстура pytest для перехвата вывода в консоль.
    """
    empty_df = pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория", "Описание"])

    with (
        patch("src.main.load_transactions", return_value=empty_df),
        patch("src.main.main_page", return_value="Доброе утро!"),
        patch("src.main.investment_bank", return_value=0),
        patch("src.main.spending_by_category", return_value="[]"),
    ):
        main()
        captured = capsys.readouterr()

        # Проверяем, что выводится сообщение об отсутствии транзакций
        assert "Нет транзакций по категории «Супермаркеты» за последние 3 месяца." in captured.out


def test_main_json_decode_error(capsys: CaptureFixture) -> None:
    """
    Тест обработки ошибки декодирования JSON в main().

    Имитирует ситуацию, когда spending_by_category возвращает некорректный JSON.

    Args:
        capsys: фикстура pytest для перехвата вывода в консоль.
    """
    with (
        patch("src.main.load_transactions", return_value=pd.DataFrame()),
        patch("src.main.main_page", return_value="Доброе утро!"),
        patch("src.main.investment_bank", return_value=150),
        patch("src.main.spending_by_category", return_value="некорректный json"),
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_investment_bank_exception(capsys: CaptureFixture) -> None:
    """
    Тест обработки исключения в investment_bank.

    Имитирует ошибку в расчёте инвесткопилки.

    Args:
        capsys: фикстура pytest для перехвата вывода в консоль.
    """
    with (
        patch("src.main.load_transactions", return_value=pd.DataFrame()),
        patch("src.main.main_page", return_value="Доброе утро!"),
        patch("src.main.investment_bank", side_effect=ValueError("Ошибка расчёта")),
        patch("src.main.spending_by_category", return_value="[]"),
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_load_transactions_exception(capsys: CaptureFixture) -> None:
    """
    Тест обработки исключения при загрузке транзакций.

    Имитирует ошибку загрузки данных из Excel‑файла.

    Args:
        capsys: фикстура pytest для перехвата вывода в консоль.
    """
    with (
        patch("src.main.load_transactions", side_effect=FileNotFoundError("Файл не найден")),
        patch("src.main.main_page", return_value="Доброе утро!"),
        patch("src.main.investment_bank", return_value=150),
        patch("src.main.spending_by_category", return_value="[]"),
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
