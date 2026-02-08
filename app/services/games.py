import dataclasses
import typing as t
from dataclasses import dataclass

from app import config, data, logger
from app.db import Game as GameTable
from app.db import User, UserGame
from app.repr import auto_repr
from app.services import audit


@dataclass
@auto_repr("slug", "name")
class Game:
    @dataclass
    class Poster:

        @dataclass
        class Colors:
            main: str = "#330000"
            accent: str = "#333333"

        @dataclass
        class Game:
            name: str
            type: t.Literal["pc", "console", "mobile"]
            subtext: str
            description: str

        @dataclass
        class Controller:
            name: str
            price: str
            description: str
            image: str

        @dataclass
        class ControllersNotes:
            extras: list[str] = dataclasses.field(default_factory=list)
            shipping: dict[str, str] = dataclasses.field(default_factory=dict)

        colors: Colors = dataclasses.field(default_factory=Colors)
        description: str = None
        games: list[Game] = dataclasses.field(default_factory=list)
        controllers: list[Controller] = dataclasses.field(default_factory=list)
        controllers_notes: ControllersNotes = None

    slug: str
    name: str
    image: str = None
    igdb: list[str] = None
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
    def poster(self) -> Poster:
        from app import app

        data = app.data.get("games_posters", {}).get(self.slug, {})
        return self.Poster(
            **{
                field.name: data.get(field.name)
                for field in dataclasses.fields(self.Poster)
                if field.name in data
            }
        )

    @property
    def platforms_short(self):
        if not self.platforms:
            return []

        return sorted(
            set(
                "Console" if key in self.platforms_console else key
                for key in self.platforms
            )
        )

    @property
    def platforms_console(self):
        from app import app

        if not self.platforms:
            return []

        platforms = app.data.get("platforms", {})
        return sorted(
            set(
                platform
                for platform in self.platforms
                if platforms.get(platform, {}).get("console", True)
            )
        )

    @property
    def platforms_smart(self):
        if len(self.platforms_console) > 1:
            return self.platforms_short
        return self.platforms

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
                logger.info(f"Populating DB with game {game}")
        s.commit()


def add_to_list(slug: str, user: User, discord=True) -> bool:
    from app import app
    from app.services import discord as discord_service

    game = get(slug)
    with app.session() as s:
        action = s.greate(
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


def get_platforms() -> list[str]:
    from app import app

    return sorted(
        set(
            "Console" if value.get("console", True) else key
            for key, value in app.data.get("platforms", {}).items()
        )
    )
