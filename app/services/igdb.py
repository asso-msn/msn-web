# From: https://github.com/Tina-otoge/withoutbait-web/blob/master/app/cli/igdb_seed.py  # noqa: E501

import dataclasses
import datetime
import typing as t
from enum import Enum

import requests
from pydantic import BaseModel as Model

from app import config

API_URL = "https://api.igdb.com/v4/"
TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/token"


class API:
    def __init__(
        self,
        client_id=config.TWITCH_CLIENT_ID,
        client_secret=config.TWITCH_CLIENT_SECRET,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self._auth_token = None

    @property
    def auth_token(self):
        if self._auth_token:
            return self._auth_token

        response = requests.post(
            TWITCH_AUTH_URL,
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
        )
        self._auth_token = response.json()["access_token"]
        return self.auth_token

    def request(self, endpoint: str, *commands: str):
        result = requests.post(
            f"{API_URL}{endpoint}",
            ";".join(commands) + ";",
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Client-ID": self.client_id,
            },
        )
        if not result.ok:
            raise Exception(result.content.decode())
        return result.json()

    class Platform(Model):
        id: int
        slug: str
        name: str = None

    def get_platforms(self, search=None, with_name=False) -> list[Platform]:
        fields = "id, slug"
        if with_name:
            fields += ", name"

        data = self.request(
            "platforms",
            f"fields {fields}",
            "limit 500",
            f'search "{search}"' if search else "",
        )
        return [self.Platform(**platform) for platform in data]

    class Collection(Model):
        id: int
        name: str

    class Game(Model):
        FIELDS: t.ClassVar = (
            "name, slug, first_release_date, platforms.slug, collection.name"
        )

        class Category(Enum):
            MAIN_GAME = 0
            DLC = 1
            FORK = 12
            ...

            def __str__(self):
                return str(self.value)

        name: str
        slug: str
        platforms: list["API.Platform"] = dataclasses.field(
            default_factory=list
        )
        first_release_date: datetime.datetime = None
        collection: "API.Collection" = None

    def get_game(self, slug: str) -> Game:
        data = self.request(
            "games",
            f"fields {self.Game.FIELDS}",
            f'where slug = "{slug}"',
            "limit 1",
        )
        if not data:
            return None
        return self.Game(**data[0])

    def get_games(self, query, safe=False, limit=100, match=True) -> list[Game]:
        """
        match: If True, only return games where the query is inside the title or
            collection name.
        """
        if not safe:
            query = query.replace(";{}\"'", "")

        data = self.request(
            "games",
            f"fields {self.Game.FIELDS}",
            f'search "{query}"',
            "where category = "
            f"    ({self.Game.Category.MAIN_GAME}, {self.Game.Category.FORK})",
            f"limit {limit}",
        )
        result = [self.Game(**game) for game in data]

        if match:
            result = [
                game
                for game in result
                if (
                    query.lower() in game.name.lower()
                    or (
                        game.collection
                        and query.lower() in game.collection.name.lower()
                    )
                )
            ]

        return result
