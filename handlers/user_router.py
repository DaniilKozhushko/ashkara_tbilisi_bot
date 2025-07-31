import db.funcs as f
import db.models as m
import utils.utils as u
import keyboards.reply as rkb
from config import settings
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup


# роутер для обработки сообщений от пользователей
user_router = Router()


# обработчик команды /start
@user_router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    # проверка нахождения пользователя в базе данных
    if await f.user_exists(message.from_user.id):
        await message.answer(text=f"Приветствую тебя снова, {message.from_user.first_name}!")

        # проверка авторизации пользователя
        if await f.is_authorized(message.from_user.id):
            await select_command(message, state)
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
        await select_command(message, state)
    else:
        await message.reply(
            text=f"""😢 Код неправильный.

Попробуй ещё раз ⬇️"""
        )
        return


# обработчик команды /select
@user_router.message(Command("select"))
async def select_command(message: Message, state: FSMContext):
    if await f.is_authorized(message.from_user.id):
        await message.answer(text="Выбери желаемый раздел:", reply_markup=rkb.select())
    else:
        # предложение пользователю авторизоваться
        await sign_up_command(message, state)


# обработчик кнопки 'Инструкция'
@user_router.message(F.text == "🙋🏼‍♂️ Инструкция")
async def instruction_button(message: Message, state: FSMContext):
    # проверка авторизации пользователя
    if await f.is_authorized(message.from_user.id):
        await about_command(message, state)
    else:
        # предложение пользователю авторизоваться
        await sign_up_command(message, state)


# обработчик кнопки 'Добавить списание'
@user_router.message(F.text == "📋 Добавить списание")
async def add_write_off_button(message: Message, state: FSMContext):
    # проверка авторизации пользователя
    if await f.is_authorized(message.from_user.id):
        await write_off_command(message, state)
    else:
        # предложение пользователю авторизоваться
        await sign_up_command(message, state)


# обработчик команды /about
@user_router.message(Command("about"))
async def about_command(message: Message, state: FSMContext):
    # проверка авторизации пользователя
    if await f.is_authorized(message.from_user.id):
        await message.answer(
            text=f"""Чтобы сделать списание, отправь сообщение в следующем формате:

<b>дата</b>
<b>тип списания</b>
<b>комментарий</b>
<b>продукт</b> <b>количество</b> <b>ед.измерения</b>"""
        )
        await message.answer(text="Например:")
        await message.answer(
            text=f"""04.06.2025
стафф
-
молоко 3 л
куриное филе п/ф 2 кг"""
        )
        await message.answer(
            text=f"""05.07.2026
прочее
Дани забрал себе домой
яйца 20 шт
сахар 3,5 кг"""
        )
        await state.clear()
        await select_command(message, state)
    else:
        # предложение пользователю авторизоваться
        await sign_up_command(message, state)


# класс Состояний для команды /write_off
class WriteOff(StatesGroup):
    making_write_off = State()


# обработчик команды /write_off
@user_router.message(Command("write_off"))
async def write_off_command(message: Message, state: FSMContext):
    # проверка авторизации пользователя
    if await f.is_authorized(message.from_user.id):
        await message.answer(text="Чтобы сделать списание - введи его и отправь")

        # переход в режим Состояния
        await state.set_state(WriteOff.making_write_off)
    else:
        # предложение пользователю авторизоваться
        await sign_up_command(message, state)


# получение списания от пользователя
@user_router.message(WriteOff.making_write_off)
async def making_write_off_state(message: Message, state: FSMContext):
    # сохранение текста пользователя
    text = message.text

    try:
        parsed_text = u.parse_write_off(message.from_user.id, text)
    except ValueError as e:
        await message.reply(text=f"""Ошибка:
{e}
Попробуй ещё раз.""")
        return

    await f.add_write_off(parsed_text)
    await state.clear()
    await message.reply(text="Списание успешно добавлено!")
    await select_command(message, state)


# обработчик неизвестных сообщений
@user_router.message(StateFilter(None))
async def unknown_message(message: Message, state: FSMContext):
    # проверка авторизации пользователя
    if await f.is_authorized(message.from_user.id):
        await message.answer("Я тебя не понял. Используй /about или /write_off")
        await state.clear()
        await select_command(message, state)
    else:
        # предложение пользователю авторизоваться
        await sign_up_command(message, state)