import os
from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass
class Config:
    SERVER_NAME: str
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    ARROW_LANG: str = "fr"
    AVATAR_SIZE: int = 256
    DISCORD_AVATAR_SIZE: int = AVATAR_SIZE
    GRAVATAR_AVATAR_SIZE: int = AVATAR_SIZE

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
