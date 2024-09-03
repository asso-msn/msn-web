import dataclasses
import logging
from dataclasses import dataclass

from app import config, data, db
from app.db import Game as GameTable
from app.db import User, UserGame
from app.services import audit


@dataclass
class Game:
    @dataclass
    class Colors:
        main: str
        accent: str

    slug: str
    name: str
    image: str = None
    igdb: list[str] = None
    colors: Colors = None
    start: int = None
    end: int = None
    publisher: str = None
    platforms: list[str] = dataclasses.field(default_factory=list)
    description_short: str = None
    description: str = None
    popular: bool = False

    def __post_init__(self):
        self._db = None

    def __str__(self):
        return self.name

    @property
    def image_url(self):

        return f"{config.CLOUD_ASSETS_URL}/games/{self.image}"

    @property
    def page(self) -> bool:
        from app import app

        return self.slug in app.data.get("games_pages", [])

    @property
    def poster(self):
        from app import app

        return app.data["games_posters"].get(self.slug)

    @property
    def platforms_short(self):
        from app import app

        if not self.platforms:
            return []

        platforms = app.data.get("platforms", {})
        return sorted(
            set(
                "Console" if value.get("console", True) else key
                for key, value in platforms.items()
                if key in self.platforms
            )
        )

    @property
    def path(self):
        return data.resolve(f"games/{self.slug}.yml")

    @property
    def db(self):
        if self._db is None:
            self.load_db()
        return self._db

    def load_db(self, *args):
        from app import app

        with app.session() as s:
            self._db = s.query(GameTable).filter(GameTable.slug == self.slug)
            if args:
                self._db = self._db.options(*args)
            self._db = self._db.first()


def get(slug: str) -> Game | None:
    from app import app

    fields = [x.name for x in dataclasses.fields(Game)]
    game_data = app.data.get("games", {}).get(slug)

    if not game_data:
        return None

    return Game(
        **{key: value for key, value in game_data.items() if key in fields},
        slug=slug,
    )


def get_by_name(name: str) -> Game | None:
    for game in get_all():
        if game.name == name:
            return game


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


def get_slugs() -> list[str]:
    from app import app

    return app.data.get("games", {}).keys()


def get_popular(limit=10, sort=None) -> list[Game]:
    return [game for game in get_all(sort=sort) if game.popular][:limit]


def populate():
    from app import app

    with app.session() as s:
        for game in get_all():
            if not game.db:
                s.add(GameTable(slug=game.slug))
                logging.info(f"Populating DB with game {game}")
        s.commit()


def add_to_list(slug: str, user: User, discord=True) -> bool:
    from app import app
    from app.services import discord as discord_service

    game = get(slug)
    with app.session() as s:
        action = db.greate(
            s,
            UserGame,
            filter={"user_id": user.id, "game_id": game.db.id},
        )
        if action.created:
            s.commit()
            audit.log(f"Game {game} added to {user}")
            if discord:
                discord_service.add_game(user, game)
    return action.created


def remove_from_list(slug: str, user: User, discord=True) -> bool:
    from app import app
    from app.services import discord as discord_service

    game = get(slug)
    with app.session() as s:
        query = s.query(UserGame).filter_by(user_id=user.id, game_id=game.db.id)
        exists = bool(query.first())
        if exists:
            query.delete()
            s.commit()
            audit.log(f"Game {game} removed to {user}")
            if discord:
                discord_service.remove_game(user, game)
    return exists


def set_favorite(slug: str, user: User, favorite: bool) -> bool:
    from app import app

    game = get(slug)
    with app.session() as s:
        instance = (
            s.query(UserGame)
            .filter_by(user_id=user.id, game_id=game.db.id)
            .first()
        )
        different = instance.favorite != favorite
        if different:
            instance.favorite = favorite
            s.commit()
            audit.log(f"Game {game} favorite set to {favorite} for {user}")
    return different
