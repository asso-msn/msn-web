import enum

from flask_login import UserMixin

from . import Column, Id, Table, Timed, column


class User(Table, UserMixin, Id, Timed):
    class ImageType(enum.StrEnum):
        local = enum.auto()
        gravatar = enum.auto()
        discord = enum.auto()

    login: Column[str] = column(unique=True)
    email: Column[str | None]
    password: Column[str | None]
    display_name: Column[str | None]
    bio: Column[str | None]
    image: Column[str | None]
    image_type: Column[ImageType] = column(default=ImageType.local)

    discord_id: Column[str | None]
    discord_access_token: Column[str | None]
    discord_refresh_token: Column[str | None]

    def __str__(self):
        return self.display_name or self.login
