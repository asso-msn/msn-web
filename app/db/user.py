import enum

from flask_login import UserMixin

from . import Column, Table, column


class User(Table, UserMixin):
    class ImageType(enum.StrEnum):
        local = enum.auto()
        gravatar = enum.auto()
        discord = enum.auto()

    id: Column[str] = column(primary_key=True)
    email: Column[str | None]
    password: Column[str | None]
    display_name: Column[str | None]
    bio: Column[str | None]
    image: Column[str | None]

    @property
    def name(self) -> str:
        return self.display_name or self.id
