from datetime import UTC, datetime

import humps
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped as Column
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_mixin as mixin
from sqlalchemy.orm import mapped_column as column

from app import VAR_DIR

engine = sa.create_engine(f"sqlite:///{VAR_DIR / 'app.db'}")


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


@mixin
class Id:
    id: Column[int] = column(primary_key=True)


@mixin
class Timed:
    created_at: Column[datetime] = column(default=lambda: datetime.now(UTC))
    updated_at: Column[datetime | None] = column(
        onupdate=lambda: datetime.now(UTC)
    )


from .user import User  # noqa: E402
