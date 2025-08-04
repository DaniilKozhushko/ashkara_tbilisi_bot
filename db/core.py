from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# асинхронный движок SQLAlchemy, который работает через asyncpg - драйвер PostgreSQL для асинхронного доступа к базе данных
async_engine = create_async_engine(settings.database_url_asyncpg, echo=True)

# фабрика сессий для работы с базой данных в асинхронном режиме
async_session = async_sessionmaker(async_engine)
