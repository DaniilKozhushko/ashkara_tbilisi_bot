import db.models as m
import utils.utils as u
from db.models import Base
from datetime import datetime
from db.core import async_engine
from db.core import async_session
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert


async def init_db(drop: bool = False) -> None:
    """
    Инициализирует базу данных.

    Если параметр drop установлен True, то перед созданием существующие таблицы будут удалены.

    :param drop: True, если необходимо удалить все таблицы перед созданием, иначе False
    :return: None
    """

    async with async_engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        await init_write_off_types(session)
        await init_units_of_measurement(session)


async def user_exists(user_id: int) -> bool:
    """
    Проверяет, существует ли пользователь с данным user_id в базе данных.

    :param user_id: id пользователя, которого нужно проверить
    :return: True, если пользователь найден, иначе False
    """

    async with async_session() as session:
        query = select(m.UsersOrm).where(m.UsersOrm.id == user_id)
        result = await session.execute(query)
        return result.scalar() is not None


async def add_user(user: m.UsersOrm) -> None:
    """
    Добавляет нового пользователя в базу данных.

    :param user: объект модели UsersOrm с данными пользователя: id, username, first_name, last_name, registration_date, code, is_authorized
    :return: None
    """

    async with async_session() as session:
        async with session.begin():
            stmt = (
                insert(m.UsersOrm)
                .values(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    registration_date=user.registration_date,
                    code=user.code,
                    is_authorized=user.is_authorized,
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )

            await session.execute(stmt)


async def get_code(user_id: int) -> str:
    """
    Возвращает код авторизации пользователя из базы данных.

    :param user_id: id пользователя, код которого нужно получить
    :return: str
    """

    async with async_session() as session:
        code = await session.scalar(
            select(m.UsersOrm.code).where(m.UsersOrm.id == user_id)
        )
    return code


async def authorize_user(user_id: int) -> None:
    """
    Авторизует пользователя.

    :param user_id: id пользователя, которого нужно авторизовать
    :return: None
    """

    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(m.UsersOrm)
                .where(m.UsersOrm.id == user_id)
                .values(is_authorized=True)
            )


async def is_authorized(user_id: int) -> bool:
    """
    Проверяет, авторизован ли пользователь с данным id.

    :param user_id: id пользователя, авторизацию которого нужно проверить
    :return: bool
    """

    async with async_session() as session:
        result = await session.scalar(
            select(m.UsersOrm.is_authorized).where(m.UsersOrm.id == user_id)
        )
        return bool(result)


async def add_write_off(
    parsed_data: list[tuple[int, str, str, str, float, str, datetime]],
) -> None:
    """
    Добавляет новые записи в таблицу списаний.

    :param parsed_data: list список кортежей списаний
    :return: None
    """
    # получение id типа списания
    type_id = await get_write_off_type_id(parsed_data[0][1])

    async with async_session() as session:
        async with session.begin():
            for row in parsed_data:
                # получение id единицы измерения
                unit_id = await get_unit_of_measurement_id(row[5])

                stmt = insert(m.WriteOffsOrm).values(
                    user_id=row[0],
                    type=type_id,
                    product=row[3],
                    quantity=row[4],
                    units=unit_id,
                    comment=row[2],
                    users_date=row[6],
                    date=u.get_utc_time(),
                )
                await session.execute(stmt)


async def init_write_off_types(session: AsyncSession) -> None:
    """
    Заполняет таблицу write_off_types базовыми значениями.

    :return: None
    """

    types = [{"name": "staff"}, {"name": "waste"}, {"name": "other"}]
    for type in types:
        exists = await session.scalar(
            select(m.WriteOffTypesOrm).where(m.WriteOffTypesOrm.name == type["name"])
        )
        if not exists:
            session.add(m.WriteOffTypesOrm(**type))
    await session.commit()


async def init_units_of_measurement(session: AsyncSession) -> None:
    """
    Заполняет таблицу units_of_measurement базовыми значениями.

    :return: None
    """

    units = [{"name": "kg"}, {"name": "l"}, {"name": "pcs"}, {"name": "gr"}]
    for unit in units:
        exists = await session.scalar(
            select(m.UnitsOfMeasurementOrm).where(
                m.UnitsOfMeasurementOrm.name == unit["name"]
            )
        )
        if not exists:
            session.add(m.UnitsOfMeasurementOrm(**unit))
    await session.commit()


async def get_write_off_type_id(type_name: str) -> int:
    """
    Возвращает id запрашиваемого типа из таблицы write_off_types.

    :return: int
    """
    async with async_session() as session:
        type_id = await session.scalar(
            select(m.WriteOffTypesOrm.id).where(m.WriteOffTypesOrm.name == type_name)
        )
    return type_id


async def get_unit_of_measurement_id(unit_name: str) -> int:
    """
    Возвращает id запрашиваемых единиц измерения из таблицы units_of_measurement.

    :return: int
    """
    async with async_session() as session:
        unit_id = await session.scalar(
            select(m.UnitsOfMeasurementOrm.id).where(
                m.UnitsOfMeasurementOrm.name == unit_name
            )
        )
    return unit_id
