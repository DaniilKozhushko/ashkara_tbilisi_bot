import asyncio
from aiogram import Bot
from config import settings
from db.funcs import init_db
from aiogram import Dispatcher
from aiogram.enums import ParseMode
from handlers.user_router import user_router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from middlewares.clear_state import AutoClearStateMiddleware
from middlewares.authorization import AuthorizationMiddleware

# инициализация объекта Бота с токеном с указанием форматирования сообщений
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


# инициализация объекта Диспетчера с хранилищем в памяти
dp = Dispatcher(storage=MemoryStorage())


# главная асинхронная функция для запуска бота
async def main():
    # подключение роутера
    dp.include_router(user_router)

    # подключение middleware в нужном порядке
    dp.message.middleware(AuthorizationMiddleware())
    dp.message.middleware(AutoClearStateMiddleware())

    # инициализация базы данных
    await init_db(drop=True)

    try:
        # очистка старых обновлений, чтобы бот не обработал старые команды после запуска
        await bot.delete_webhook(drop_pending_updates=True)

        # запуск long polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # корректное закрытие сессии после завершения работы бота
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
