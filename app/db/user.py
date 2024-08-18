import enum
import hashlib
from datetime import datetime

import flask
from flask_login import UserMixin

from app.services import audit

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
    last_seen: Column[datetime | None]

    discord_id: Column[str | None]
    discord_access_token: Column[str | None]
    discord_refresh_token: Column[str | None]

    hide_in_list: Column[bool] = column(default=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(login={self.login}, id={self.id})"

    def __str__(self):
        return self.display_name or self.login

    @property
    def avatar_url(self) -> str:
        from app import config

        if self.image and self.image_type == User.ImageType.local:
            return flask.url_for("avatar", hash=self.image)
        size = config.GRAVATAR_AVATAR_SIZE
        return self.image or f"https://www.gravatar.com/avatar/?s={size}&d=mp"

    def reset_avatar(self):
        self.image = None
        self.image_type = User.ImageType.local

    def refresh_avatar(self):
        from app import config

        if self.image_type == User.ImageType.discord:
            from app.services import discord

            api = discord.API(self.discord_access_token)
            user = api.get_user()
            if self.image == user.avatar_url:
                return False
            audit.log("Discord avatar refreshed", user=self)
            self.image = user.avatar_url
            return True

        if self.image_type == User.ImageType.gravatar:
            email = self.email.lower()
            email_hash = hashlib.sha256(email.encode()).hexdigest()
            size = config.GRAVATAR_AVATAR_SIZE
            self.image = (
                f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=mp"
            )
            return

    @property
    def has_discord(self) -> bool:
        return bool(self.discord_id)

    def refresh_discord_token(self):
        from app.services import discord

        response = discord.refresh(self.discord_refresh_token)
        if self.discord_access_token == response.access_token:
            return False
        self.discord_access_token = response.access_token
        self.discord_refresh_token = response.refresh_token
        return True
