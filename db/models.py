from typing import Optional
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    SmallInteger,
    Text,
    Integer,
    Float,
)


class Base(DeclarativeBase):
    """
    Базовый класс для всех ORM-моделей. От него наследуются конкретные таблицы.
    """

    pass


class UsersOrm(Base):
    """
    Модель таблицы users.
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    registration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    code: Mapped[str] = mapped_column(String(8), nullable=False)
    is_authorized: Mapped[bool] = mapped_column(Boolean, nullable=False)


class WriteOffTypesOrm(Base):
    """
    Модель таблицы write_off_types.
    """

    __tablename__ = "write_off_types"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(5), unique=True, nullable=False)


class UnitsOfMeasurementOrm(Base):
    """
    Модель таблицы units_of_measurement.
    """

    __tablename__ = "units_of_measurement"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)


class WriteOffsOrm(Base):
    """
    Модель таблицы write_offs.
    """

    __tablename__ = "write_offs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), autoincrement=False, nullable=False
    )
    type: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("write_off_types.id"), nullable=False
    )
    product: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    units: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("units_of_measurement.id"), nullable=False
    )
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    users_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
