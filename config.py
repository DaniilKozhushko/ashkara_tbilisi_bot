from pydantic_settings import BaseSettings, SettingsConfigDict


# класс Settings автоматически подгружает переменные окружения из .env файла
class Settings(BaseSettings):
    # обязательные поля, значения которых будут браться из переменных окружения или .env файла
    TELEGRAM_BOT_TOKEN: str
    ADMIN_ID: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    @property
    def database_url_asyncpg(self) -> str:
        """
        Формирует строку подключения для SQLAlchemy с использованием драйвера asyncpg. Используется для асинхронной работы с PostgreSQL.

        :return: None
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
