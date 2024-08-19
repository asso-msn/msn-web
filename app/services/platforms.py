from dataclasses import dataclass

from app import app


@dataclass
class Platform:
    name: str
    console: bool
    _igdb: list[str] = None

    @property
    def igdbs(self):
        if not self._igdb:
            return [self.name.lower().replace(" ", "")]
        return self._igdb


def get_platforms():
    data = app.data.get("platforms", {})
    return [
        Platform(
            name=key,
            console=value.get("console", True),
            _igdb=value.get("igdb"),
        )
        for key, value in data.items()
    ]


def get_by_slug(slug):
    return get_platforms_by_slug().get(slug)


def get_platforms_by_slug(slug=None) -> dict[str, Platform]:
    result = {}
    for platform in get_platforms():
        for igdb_slug in platform.igdb:
            result[igdb_slug] = platform
    return result
