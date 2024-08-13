import enum
import hashlib

from flask_login import UserMixin

from . import Column, Id, Table, Timed, column


class User(Table, UserMixin, Id, Timed):
    class ImageType(enum.StrEnum):
        # local = enum.auto()
        gravatar = enum.auto()
        discord = enum.auto()

    login: Column[str] = column(unique=True)
    email: Column[str | None]
    password: Column[str | None]
    display_name: Column[str | None]
    bio: Column[str | None]
    image: Column[str | None]
    image_type: Column[ImageType | None]
    # image_type: Column[ImageType] = column(default=ImageType.local)

    discord_id: Column[str | None]
    discord_access_token: Column[str | None]
    discord_refresh_token: Column[str | None]

    def __str__(self):
        return self.display_name or self.login

    @property
    def avatar_url(self):
        return self.image or "https://www.gravatar.com/avatar/?d=mp"

    def update_avatar(self):
        if self.image_type == User.ImageType.discord:
            from app.services import discord

            api = discord.API(self.discord_access_token)
            user = api.get_user()
            self.image = user.avatar_url
            return

        if self.image_type == User.ImageType.gravatar:
            email_hash = hashlib.sha256(self.email.lower().encode()).hexdigest()
            self.image = f"https://www.gravatar.com/avatar/{email_hash}?d=mp"
            return

    def refresh_discord_token(self):
        from app.services import discord

        response = discord.refresh(self.discord_refresh_token)
        self.discord_access_token = response.access_token
        self.discord_refresh_token = response.refresh_token
