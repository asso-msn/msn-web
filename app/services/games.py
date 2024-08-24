import dataclasses
import logging
from dataclasses import dataclass

from app import data
from app.db import Game as GameTable


@dataclass
class Game:
    @dataclass
    class Colors:
        main: str
        accent: str

    slug: str
    name: str
    igdb: list[str] = None
    colors: Colors = None
    start: int = None
    end: int = None
    publisher: str = None
    platforms: list[str] = None
    description: str = None

    def __str__(self):
        return self.name

    @property
    def path(self):
        return data.resolve(f"games/{self.slug}.yml")

    @property
    def db(self):
        from app import app

        with app.session() as s:
            return (
                s.query(GameTable).filter(GameTable.slug == self.slug).first()
            )


def get(slug: str) -> Game:
    from app import app

    fields = [x.name for x in dataclasses.fields(Game)]
    game_data = app.data.get("games", {}).get(slug)

    return Game(
        **{key: value for key, value in game_data.items() if key in fields},
        slug=slug,
    )


def get_all(sort=None) -> list[Game]:
    from app import app

    result = [get(slug) for slug in app.data.get("games", {})]
    if sort:

        def sort_key(game):
            x = getattr(game, sort)
            if isinstance(x, str):
                x = x.lower()
            return x

        result.sort(key=sort_key)
    return result


def populate():
    from app import app

    with app.session() as s:
        for game in get_all():
            if not game.db:
                s.add(GameTable(slug=game.slug))
                logging.info(f"Populating DB with game {game}")
        s.commit()
