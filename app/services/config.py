import dataclasses
import os
from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass
class Config:
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    ARROW_LANG: str = "fr"
    AUDIT_WEBHOOK: str = None
    AVATAR_SIZE: int = 256
    DISCORD_AVATAR_SIZE: int = AVATAR_SIZE
    DISCORD_BOT_TOKEN: str = None
    DISCORD_SERVER_ID: str = None
    GRAVATAR_AVATAR_SIZE: int = AVATAR_SIZE
    SERVER_NAME: str = "localhost:5000"
    CLOUD_ASSETS_URL: str = "https://asso-msn.fr/assets"
    TWITCH_CLIENT_ID: str = None
    TWITCH_CLIENT_SECRET: str = None
    GAMES_SHOWCASE: list = dataclasses.field(
        default_factory=lambda: ["2dx", "ddr", "sdvx", "taiko", "popn", "gc"]
    )
    RUN_TASKS: bool = False

    @property
    def LANG(self):
        return self.ARROW_LANG

    @staticmethod
    def convert(value, type):
        if type == bool:
            return value.lower() in ["true", "1", "yes"]
        return type(value)

    @classmethod
    def load(cls, path="config.yml"):
        path = Path(path)  # 🐶
        if not path.exists():
            with path.open("w") as f:
                yaml.safe_dump(
                    {
                        field.name: getattr(cls, field.name, "REPLACE_ME")
                        for field in fields(cls)
                    },
                    f,
                )
        with path.open() as f:
            data = yaml.safe_load(f)
        for field in fields(cls):
            if field.name in os.environ:
                data[field.name] = cls.convert(
                    os.environ[field.name], field.type
                )
        return cls(**data)
