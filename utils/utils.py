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


def parse_write_off(user_id: int, text: str) -> list[tuple[int, str, str, str, float, str, datetime]]:
    """
    Парсит текст списания и возвращает его в формате:
    [(user_id, type, comment, product, quantity, unit, date), ...]

    :param user_id: id пользователя, который вносит списание
    :param text: str текст списания
    :return: list[tuple[int, str, str, str, float, str, datetime]]
    """
    result = []
    lines = text.strip().lower().split("\n")

    if len(lines) < 4:
        raise ValueError("Недостаточно строк в тексте списания.")

    # парсинг даты
    try:
        date = datetime.strptime(lines[0], "%d.%m.%Y")
    except ValueError:
        raise ValueError("Неверный формат даты. Используй ДД.ММ.ГГГГ.")

    types = {
        "staff": ["стафф", "стаф", "персонал"],
        "waste": ["порча", "списание"],
        "other": ["прочее"]
    }

    units = {
        "kg": ["кг", "кг.", "килограмм", "килограммов", "килограмма"],
        "l": ["л", "литр", "литров", "л."],
        "pcs": ["шт", "штук", "шт."],
        "gr": ["г", "грамм", "гр", "граммов", "г.", "гр."]
    }

    write_off_type = None
    for key, aliases in types.items():
        if lines[1] in aliases:
            write_off_type = key
            break

    if write_off_type is None:
        raise ValueError(f"Неизвестный тип списания: {lines[1]}")

    # комментарий
    comment = lines[2]

    # продукты
    for line in lines[3:]:
        parts = line.strip().rsplit(" ", 2)
        if len(parts) != 3:
            raise ValueError(f"Ошибка в строке: {line}")

        product, quantity_str, unit = parts

        for key, aliases in units.items():
            if unit in aliases:
                unit = key
                break

        try:
            quantity = float(quantity_str.replace(",", "."))
        except ValueError:
            raise ValueError(f"Не удалось преобразовать количество {quantity_str} в число")

        result.append((
            user_id,
            write_off_type,
            comment,
            product,
            quantity,
            unit,
            date
        ))

    return result