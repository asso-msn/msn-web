from typing import Type

import sqlalchemy as sa
from sqlalchemy import orm


def camel_to_snake(s: str) -> str:
    result = ""
    for i, c in enumerate(s):
        r = c.lower()
        if not c.isupper():
            result += r
            continue
        if i > 0 and (
            not s[i - 1].isupper()
            or (i + 1 < len(s) and not s[i + 1].isupper())
        ):
            result += "_"
        result += r
    return result


def pluralize(s: str) -> str:
    if s.endswith("s"):
        return s
    if s.endswith("h"):
        return s + "es"
    if s.endswith("y"):
        return s[:-1] + "ies"
    return s + "s"


class Base:
    REPR_KEYS = set()

    @orm.declared_attr
    def __tablename__(cls: Type):
        """
        Generate table names from class names converted from CamelCase to lower
        snake_case, with an added "s" or "ies" if it end with "y"
        Examples:
        - User -> users
        - UserSetting -> user_settings
        - Country -> countries
        """
        name = cls.__name__.removesuffix("Table")
        name = camel_to_snake(name)
        name = pluralize(name)
        if hasattr(cls, "__table_prefix__"):
            name = f"{cls.__table_prefix__}_{name}"
        return name

    def __repr__(self):
        # From https://github.com/pallets/flask-sqlalchemy/blob/main/src/flask_sqlalchemy/model.py

        identity = sa.inspect(self).identity

        if identity is None:
            pk = f"(transient {id(self)})"
        else:
            pk = ", ".join(str(value) for value in identity)

        if self.REPR_KEYS:
            pk += " " + ", ".join(
                f"{x}={getattr(self, x)}" for x in self.REPR_KEYS
            )

        return f"<{type(self).__name__} {pk}>"

    def set_slug(self, target, value, replace=True):
        from app.db import Session

        if not replace and getattr(self, target) is not None:
            return
        slug = value.lower().replace(" ", "-")
        cls = type(self)
        with Session() as session:
            if (
                session.query(type(self))
                .filter(getattr(cls, target) == slug)
                .first()
            ):
                raise Exception("Duplicate slug")
        setattr(self, target, slug)
