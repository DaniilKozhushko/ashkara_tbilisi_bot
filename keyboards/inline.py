from datetime import timedelta
from utils.utils import get_utc_time
from calendar import day_abbr, monthcalendar
from dateutil.relativedelta import relativedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def select_date(month: int = 0) -> InlineKeyboardMarkup:
    """
    Inline-клавиатура для выбора даты.

    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    # текущее время в Тбилиси
    curr_datetime = get_utc_time() + timedelta(hours=4)

    # отображаемая дата в календаре
    showed_datetime = curr_datetime + relativedelta(months=month)

    # строка с выбором месяца
    builder.row(
        InlineKeyboardButton(text="<", callback_data=f"month:{month-1}"),
        InlineKeyboardButton(
            text=f"{showed_datetime.strftime('%b %Y')}", callback_data="nothing"
        ),
        InlineKeyboardButton(text=">", callback_data=f"month:{month+1}"),
    )

    # строка с днями недели
    week_days_buttons = []
    for name in day_abbr:
        week_days_buttons.append(
            InlineKeyboardButton(text=f"{name}", callback_data="nothing")
        )
    builder.row(*week_days_buttons)

    # строки с неделями
    showed_year, showed_month = showed_datetime.year, showed_datetime.month
    for week in monthcalendar(showed_year, showed_month):
        week_row = []
        for day in week:
            week_row.append(
                InlineKeyboardButton(
                    text=f"{day if day != 0 else ' '}",
                    callback_data=f"{f'date:{day}/{showed_month}/{showed_year}' if day != 0 else 'nothing'}",
                )
            )
        builder.row(*week_row)

    return builder.as_markup()


def select_write_off_type() -> InlineKeyboardMarkup:
    """
    Inline-клавиатура для выбора причины списания.

    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Порча", callback_data="waste"),
        InlineKeyboardButton(text="Прочее", callback_data="other"),
    )
    builder.row(InlineKeyboardButton(text="Питание персонала", callback_data="staff"))

    return builder.as_markup()
