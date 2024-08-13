import os
from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass
class Config:
    SERVER_NAME: str
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    AVATAR_SIZE: int = 256
    DISCORD_AVATAR_SIZE: int = AVATAR_SIZE

    def __init__(self, path="config.yml"):
        path = Path(path)  # 🐶
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
