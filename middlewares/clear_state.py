from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any
from aiogram.fsm.context import FSMContext


class AutoClearStateMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable, event: Message, data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data.get("state")

        # если сообщение — это команда и есть активное состояние, то оно сбрасывается
        if event.text and event.text.startswith("/") and state:
            await state.clear()

        return await handler(event, data)
