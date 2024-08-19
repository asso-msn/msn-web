import dataclasses
from dataclasses import dataclass

from app import app, data


@dataclass
class Game:
    @dataclass
    class Colors:
        main: str
        accent: str

    id: str
    name: str
    igdb: list[str] = None
    colors: Colors = None
    start: int = None
    end: int = None
    publisher: str = None
    platforms: list[str] = None
    description: str = None

    @property
    def path(self):
        return data.resolve(f"games/{self.id}.yml")


def get_game(game_id: str) -> Game:
    fields = [x.name for x in dataclasses.fields(Game)]
    game_data = app.data.get("games", {}).get(game_id)

    return Game(
        **{key: value for key, value in game_data.items() if key in fields},
        id=game_id,
    )


def get_games() -> dict[str, Game]:
    return {game_id: get_game(game_id) for game_id in app.data.get("games", {})}
