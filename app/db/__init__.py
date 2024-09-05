import typing as t
from dataclasses import dataclass
from datetime import UTC, datetime

import alembic.command
import humps
import sqlalchemy as sa
from alembic.config import Config
from sqlalchemy import orm
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped as Column
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_mixin as mixin
from sqlalchemy.orm import mapped_column as column

from app import VAR_DIR

URI = f"sqlite:///{VAR_DIR / 'app.db'}"

try:
    engine = sa.create_engine(URI)
except ModuleNotFoundError as e:
    raise Exception(
        f"{e}"
        "\nPlease install the required dependencies to use the database."
        "\nFor Ubuntu: sudo apt install libsqlite3-dev"
        "\nIf you installed libsqlite after installing Python via pyenv, you"
        " also need to reinstall Python by running `pyenv install` again."
    ) from e


def session(**kwargs) -> Session:
    return Session(bind=engine, **kwargs)


class Table(DeclarativeBase):
    @orm.declared_attr
    def __tablename__(cls):
        result = humps.decamelize(cls.__name__)
        # Could use https://pypi.org/project/inflect/ but let's see how far we
        # get without it.
        if result[-1] == "s":
            result += "es"
        if result[-1] == "y":
            result = result[:-1] + "ies"
        if result[-1] != "s":
            result += "s"
        return result


def create_all():
    Table.metadata.create_all(engine)
    alembic_cfg = Config("alembic.ini")
    alembic.command.stamp(alembic_cfg, "head")


@mixin
class Id:
    id: Column[int] = column(primary_key=True)


@mixin
class Timed:
    created_at: Column[datetime] = column(default=lambda: datetime.now(UTC))
    updated_at: Column[datetime | None] = column(
        onupdate=lambda: datetime.now(UTC)
    )


@dataclass
class GetOrCreate:
    instance: t.Any
    created: bool


def greate(session, model, filter=None, defaults=None) -> GetOrCreate:
    """Get or create"""
    instance = session.query(model).filter_by(**filter).first()
    if instance:
        return GetOrCreate(instance, False)
    params = {**(filter or {}), **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    return GetOrCreate(instance, True)


from sqlalchemy.orm import relationship as relation  # noqa: E402 F401

from .game import Game  # noqa: E402 F401
from .relationships.user_game import UserGame  # noqa: E402 F401
from .user import User  # noqa: E402 F401
