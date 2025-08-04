from aiogram.types import Message
from aiogram import BaseMiddleware
from db.funcs import is_authorized
from aiogram.fsm.context import FSMContext
from handlers.user_router import Authorization
from typing import Callable, Awaitable, Dict, Any


class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # если сообщение - это текст и начинается с "/start" - пропустить любых пользователей
        if event.text and event.text.startswith("/start"):
            return await handler(event, data)

        # если сообщение - это текст, не команда и во время Состояния ввода кода - пропустить любых пользователей
        state: FSMContext = data.get("state")
        current_state = await state.get_state() if state else None
        if (
            event.text
            and not event.text.startswith("/")
            and current_state == Authorization.send_code.state
        ):
            return await handler(event, data)

        # проверка авторизации пользователя
        user_id = event.from_user.id
        if await is_authorized(user_id):
            return await handler(event, data)
        else:
            await event.reply(
                text=f"""😢 Код неправильный.

Попробуй ещё раз ⬇️
{current_state}"""
            )
            return
