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
    TWITCH_CLIENT_ID: str = None
    TWITCH_CLIENT_SECRET: str = None

    @property
    def LANG(self):
        return self.ARROW_LANG

    def __init__(self, path="config.yml"):
        path = Path(path)  # 🐶
        if not path.exists():
            with path.open("w") as f:
                yaml.safe_dump(
                    {
                        field.name: getattr(self, field.name, "REPLACE_ME")
                        for field in fields(self)
                    },
                    f,
                )
        with path.open() as f:
            data = yaml.safe_load(f)
        for field in fields(self):
            key = field.name
            value = os.environ.get(key) or data.get(key)
            if not value:
                continue
            if field.type == bool:
                value = value.lower() in ("true", "yes", "1")
            else:
                value = field.type(value)
            setattr(self, key, value)

        missing = [
            field.name
            for field in fields(self)
            if not hasattr(self, field.name)
        ]
        if missing:
            raise ValueError(f"Missing config: {missing}")
