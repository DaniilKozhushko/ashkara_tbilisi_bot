import db.funcs as f
import db.models as m
import utils.utils as u
import keyboards.reply as rkb
import keyboards.inline as ikb
from config import settings
from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove


# роутер для обработки сообщений от пользователей
user_router = Router()


# обработчик команды /start
@user_router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    # проверка нахождения пользователя в базе данных
    if await f.user_exists(message.from_user.id):
        await message.answer(
            text=f"Приветствую тебя снова, {message.from_user.first_name}!"
        )

        # проверка авторизации пользователя
        if await f.is_authorized(message.from_user.id):
            await select_command(message)
        else:
            # предложение пользователю авторизоваться
            await sign_up_command(message, state)
    else:
        # генерация кода для получения доступа к боту
        code = u.generate_code()

        # объект Пользователя, заполненный данными из Telegram-профиля
        user = m.UsersOrm(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            registration_date=u.get_utc_time(),
            code=code,
            is_authorized=False,
        )

        # отправка кода пользователя админу
        await message.bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=f"""🆕 НОВАЯ РЕГИСТРАЦИЯ 🆕

Отправь код <code>{code}</code> пользователю <b>{message.from_user.first_name}</b>""",
        )

        # добавление нового пользователя в базу данных
        await f.add_user(user)

        # предложение пользователю авторизоваться
        await sign_up_command(message, state)


# класс Состояния для процесса Авторизации
class Authorization(StatesGroup):
    send_code = State()


# обработчик команды /sign_up
@user_router.message(Command("sign_up"))
async def sign_up_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Тебе нужно пройти авторизацию. Введи код:")
    await state.set_state(Authorization.send_code)


# получение кода от пользователя
@user_router.message(Authorization.send_code)
async def send_code_state(message: Message, state: FSMContext):
    # сохранение текста пользователя
    text = message.text.strip()

    # получение кода из базы данных для проверки
    code = await f.get_code(message.from_user.id)

    # проверка кода
    if text == code:
        await f.authorize_user(message.from_user.id)
        await message.answer(
            text="Авторизация прошла успешно!",
            message_effect_id="5046509860389126442",
        )
        await message.answer(
            text=f"""👋🏻 Приветствую, {message.from_user.first_name}!

Инструкция для использования бота всегда доступна по команде /about"""
        )
        await state.clear()
        await select_command(message)
    else:
        await message.reply(
            text=f"""😢 Код неправильный.

Попробуй ещё раз ⬇️"""
        )
        return


# обработчик команды /select
@user_router.message(Command("select"))
async def select_command(message: Message):
    await message.answer(text="Выбери желаемый раздел:", reply_markup=rkb.select())


# обработчик кнопки "Инструкция"
@user_router.message(F.text == "🙋🏼‍♂️ Инструкция")
async def instruction_button(message: Message, state: FSMContext):
    await about_command(message)


# обработчик кнопки "Добавить списание"
@user_router.message(F.text == "📋 Добавить списание")
async def add_write_off_button(message: Message, state: FSMContext):
    await write_off_command(message, state)


# обработчик команды /about
@user_router.message(Command("about"))
async def about_command(message: Message):
    await message.answer(
        text=f"""Чтобы сделать списание, нажми кнопку <b>Добавить списание</b> и следуй указаниям далее:

1. Выбери дату
2. Выбери причину списания
3. Добавь комментарий, если необходимо
4. Введи список продуктов в формате:
    <b>название_продукта  количество  единицы_измерения</b>"""
    )
    await select_command(message)


# класс Состояний для команды /write_off
class WriteOff(StatesGroup):
    making_write_off = State()
    typing_comment = State()
    typing_products = State()


# обработчик команды /write_off
@user_router.message(Command("write_off"))
async def write_off_command(message: Message, state: FSMContext):
    # информационное сообщение
    msg = await message.answer(
        text="Чтобы добавить списание - следуй указаниям далее:",
        reply_markup=ReplyKeyboardRemove(),
    )

    # сохранение id сообщения для будущего удаления
    await state.update_data(to_delete_message_id=msg.message_id)

    # предложение выбрать дату списания и вывод календаря
    await message.answer(text="Выбери дату:", reply_markup=ikb.select_date())

    # переход в режим Состояния
    await state.set_state(WriteOff.making_write_off)


# выбор месяца в календаре
@user_router.callback_query(WriteOff.making_write_off, F.data.startswith("month:"))
async def change_month(callback: CallbackQuery):
    # получение числа для изменения месяца
    month = int(callback.data.split(":")[1])

    # запрет на превышение разумного выбора даты для списания
    if abs(month) > 2:
        await callback.answer(text=f"выбери более актуальную дату")
        await callback.message.edit_text(
            text="Выбери дату:",
            reply_markup=ikb.select_date(),
        )
    else:
        # предложение выбрать дату с учётом изменённого месяца
        await callback.message.edit_text(
            text="Выбери дату:",
            reply_markup=ikb.select_date(month=month),
        )


# выбор причины списания
@user_router.callback_query(WriteOff.making_write_off, F.data.startswith("date:"))
async def change_month(callback: CallbackQuery, state: FSMContext):
    # удаление информационного сообщения
    data = await state.get_data()
    to_delete_message_id = data.get("to_delete_message_id")
    await callback.bot.delete_message(
        chat_id=callback.message.chat.id, message_id=to_delete_message_id
    )

    # получение даты в строковом формате
    date_str = callback.data.split(":")[1]

    # получение дня, месяца и года в числовых форматах
    day, month, year = map(int, date_str.split("/"))

    # сохранение даты списания в памяти
    await state.update_data(write_off_date=datetime(year=year, month=month, day=day))

    # предложение выбрать причину списания
    await callback.message.edit_text(
        text=f"""Списание за <b>{day:02}.{month:02}.{year}</b>

Выбери причину списания:""",
        reply_markup=ikb.select_write_off_type(),
    )


# получение комментария от пользователя
@user_router.callback_query(
    WriteOff.making_write_off, F.data.in_({"waste", "other", "staff"})
)
async def select_type(callback: CallbackQuery, state: FSMContext):
    # сохранение причины списания
    write_off_type = callback.data
    await state.update_data(write_off_type=write_off_type)

    # получение и сохранение причины списания и даты для отображения
    data = await state.get_data()

    showed_write_off_date = (data.get("write_off_date")).strftime("%d.%m.%Y")
    await state.update_data(showed_write_off_date=showed_write_off_date)

    write_off_types = {
        "staff": "Питание персонала",
        "waste": "Порча",
        "other": "Прочее",
    }
    showed_write_off_type = write_off_types[write_off_type]
    await state.update_data(showed_write_off_type=showed_write_off_type)

    # сохранение id сообщения бота для будущего редактирования
    await state.update_data(editable_message_id=callback.message.message_id)

    # предложение ввести комментарий
    await callback.message.edit_text(
        text=f"""Списание за <b>{showed_write_off_date}</b>
Причина списания: <b>{showed_write_off_type}</b>

Введи комментарий или отправь "-":
"""
    )

    # переход в Состояние получения комментария
    await state.set_state(WriteOff.typing_comment)


# получение списка продуктов от пользователя
@user_router.message(WriteOff.typing_comment)
async def typing_comment_state(message: Message, state: FSMContext):
    # сохранение текста пользователя
    comment = message.text.strip()
    await state.update_data(comment=comment)

    # удаление сообщение пользователя
    await message.delete()

    # получение данных для отображения
    data = await state.get_data()
    showed_write_off_date = data.get("showed_write_off_date")
    showed_write_off_type = data.get("showed_write_off_type")

    # получение id сообщения бота для изменения
    editable_message_id = data.get("editable_message_id")

    # текст для отправки пользователю
    new_text = f"""Списание за <b>{showed_write_off_date}</b>
Причина списания: <b>{showed_write_off_type}</b>
Комментарий: <b>{comment}</b>

Введи список продуктов для списания.

Например:
молоко 2 л
куриное филе 7,5 кг
яйца 20 шт
"""

    # редактирование сообщения бота
    await message.bot.edit_message_text(
        chat_id=message.chat.id, message_id=editable_message_id, text=new_text
    )

    # переход в Состояние получения списка продуктов
    await state.set_state(WriteOff.typing_products)


# обработка и занесение списаний в БД
@user_router.message(WriteOff.typing_products)
async def typing_products_state(message: Message, state: FSMContext):
    # сохранение текста пользователя
    product_list = message.text.strip()

    # получение сохранённых данных
    data = await state.get_data()
    user_id = message.from_user.id
    write_off_type = data.get("write_off_type")
    comment = data.get("comment")
    write_off_date = data.get("write_off_date")
    editable_message_id = data.get("editable_message_id")
    showed_write_off_date = data.get("showed_write_off_date")
    showed_write_off_type = data.get("showed_write_off_type")

    # попытка парсинга
    try:
        parsed_data = u.parsing_product_list(
            user_id=user_id,
            write_off_type=write_off_type,
            comment=comment,
            product_list=product_list,
            date=write_off_date,
        )

        # редактирование сообщения бота
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=editable_message_id,
            text=f"""✅ Списание успешно добавлено

<pre>{showed_write_off_date} >>> {showed_write_off_type}
_______________
{product_list}
_______________
{comment}</pre>""",
        )

        # удаление сообщения пользователя
        await message.delete()

        # сохранение списания в БД
        await f.add_write_off(parsed_data)

        # очистка состояния и переход в главное меню
        await state.clear()
        await select_command(message)

    except ValueError as e:
        await message.answer(text=f"⚠️ {e}")


# обработчик неизвестных сообщений
@user_router.message(StateFilter(None))
async def unknown_message(message: Message, state: FSMContext):
    await message.answer("Я тебя не понял. Используй /about или /write_off")
    await state.clear()
    await select_command(message)


# обработчик callback "nothing"
@user_router.callback_query(F.data == "nothing")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
