from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def select() -> ReplyKeyboardMarkup:
    """
    Reply-клавиатура с кнопками "Инструкция" и "Добавить списание".

    :return: ReplyKeyboardMarkup
    """

    button = [
        [KeyboardButton(text="📋 Добавить списание")],
        [KeyboardButton(text="🙋🏼‍♂️ Инструкция")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=button,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Хочешь добавить списание?",
    )
