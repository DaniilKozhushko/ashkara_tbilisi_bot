import string
from random import choices
from datetime import datetime, UTC


def get_utc_time() -> datetime:
    """
    Возвращает текущее время в формате UTC.

    :return: объект datetime с временной зоной UTC
    """
    return datetime.now(UTC)


def generate_code() -> str:
    """
    Возвращает строку из 8 символов (случайно выбранные цифры и буквы английского алфавита)

    :return: str
    """
    return "".join(choices(string.ascii_letters + string.digits, k=8))


def parsing_product_list(
    user_id: int, write_off_type: str, comment: str, product_list: str, date: datetime
) -> list[tuple[int, str, str, str, float, str, datetime]]:
    """
    Парсит текст списания и возвращает его в формате:
    [(user_id, type, comment, product, quantity, unit, date), ...]

    :param user_id: id пользователя, который вносит списание
    :param write_off_type: тип списания
    :param comment: текст комментария
    :param  product_list: список продуктов для списания
    :param date: дата списания
    :return: list[tuple[int, str, str, str, float, str, datetime]]
    """
    # разбивка текста на строки
    lines = product_list.strip().lower().split("\n")

    # словарь возможных единиц измерения
    units = {
        "kg": ["кг", "кг.", "килограмм", "килограммов", "килограмма"],
        "l": ["л", "литр", "литров", "л."],
        "pcs": ["шт", "штук", "шт."],
        "gr": ["г", "грамм", "гр", "граммов", "г.", "гр.", "грамма"],
    }

    result = []

    # построчный анализ
    for line in lines:
        parts = line.strip().rsplit(" ", 2)
        if len(parts) != 3:
            raise ValueError(f"Ошибка в строке: {line}")

        product, quantity_str, unit = parts

        # получение единиц измерения
        for key, aliases in units.items():
            if unit in aliases:
                unit = key
                break
        else:
            raise ValueError(f"Неизвестная единица измерения: {unit}")

        # получение количества
        try:
            quantity = float(quantity_str.replace(",", "."))
            if quantity <= 0:
                raise ValueError(f"Количество должно быть больше нуля: {quantity_str}")
        except ValueError:
            raise ValueError(f"Ошибка количества: {quantity_str}")

        result.append((user_id, write_off_type, comment, product, quantity, unit, date))

    return result
