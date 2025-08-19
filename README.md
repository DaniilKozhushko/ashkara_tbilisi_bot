# ashkara_tbilisi_bot
Telegram-бот для приёма и учёта списаний на производстве.  
Позволяет сотрудникам добавлять списания продуктов, после чего сохраняет в базу данных PostgreSQL.
Для доступа необходимо пройти аутентификацию.
<div align="right">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="python logo"  />
  <img width="2" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" height="40" alt="postgresql logo"  />
  <img width="2" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" height="50" alt="docker logo"  />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg" height="40" alt="linux logo"  />
  <img width="2" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" height="40" alt="git logo"  />
</div>


## 🛠️ Заказ и цель проекта
Этот Telegram-бот был разработан по просьбе руководителей предприятия с целью автоматизации учёта списаний продуктов на производстве. Идея заключалась во внедрении удобного и быстрого инструмента для контроля и регистрации списаний, чтобы повысить точность учёта и снизить потери.

## ⭐️ Возможности
Пользователь (сотрудник производства) выбирает дату, тип списания, добавляет список продуктов и, по необходимости, комментарий.

## ⚙️ Технологии
- `Python` 3.11+
- `Aiogram` 3+
- `PostgreSQL` + `SQLAlchemy`
- `asyncpg`, `alembic`

## 🗂 Структура проекта

```
.
├── db/ # Работа с базой данных
│   ├── core.py # Асинхронная сессия, engine
│   ├── funcs.py # CRUD-функции для работы с БД
│   └── models.py # SQLAlchemy модели таблиц
├── handlers/ # Хэндлеры бота
│   └── user_router.py # Роутер с логикой и командами для пользователей
├── images/
├── keyboards/ # Клавиатуры для бота
│   └── reply.py # Reply-клавиатуры
│   └── inline.py # Inline-клавиатуры
├── middlewares/ # Промежуточные слои
│   └── clear_state.py # Middleware для очистки состояний FSM
│   └── authorization.py # Middleware для проверки авторизации
├── utils/ # Вспомогательные функции
│   └── utils.py # Функции генерации даты и др.
├── .env # Переменные окружения
├── .gitignore # Файлы и папки, исключённые из Git
├── config.py # # Загрузка настроек из .env через pydantic
├── docker-compose.yml # Описание сервисов (бот, БД и т.д.) для Docker Compose 
├── Dockerfile # Инструкция, как собрать контейнер с ботом
├── main.py # Точка входа: запуск бота
├── README.md # Описание проекта
└── requirements.txt # Зависимости Python-пакетов
```

## 🚀 Установка и запуск

1. Клонируй репозиторий:

   ```bash
   git clone https://github.com/DaniilKozhushko/ashkara_tbilisi_bot.git
   ```
   
   ```bash
   cd ashkara_tbilisi_bot
   ```

2. Создай .env файл:

   ```bash
   nano .env
   ```

   ```env
   TELEGRAM_BOT_TOKEN=telegram_токен_бота
   ADMIN_ID=telegram_id_админа
   DB_NAME=название_БД
   DB_USER=имя_пользователя_БД
   DB_PASSWORD=пароль_БД
   DB_HOST=db
   DB_PORT=5432
   ```

3. Собери и запусти контейнеры:
   ```bash
   docker-compose up -d --build
   ```

## 📝Лицензия

Данный проект лицензирован [MIT License](LICENSE)

![Logo_Dark](./images/logo_dark.png#gh-dark-mode-only)![Logo_Light](./images/logo_light.png#gh-light-mode-only)