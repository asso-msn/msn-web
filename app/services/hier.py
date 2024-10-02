import dataclasses
from dataclasses import dataclass

import flask


@dataclass
class Entry:
    name: str
    url: str = None
    children: list["Entry"] = dataclasses.field(default_factory=list)

    def __str__(self):
        return self.name


def get():
    return [
        Entry("L'association", flask.url_for("about")),
        Entry("Évènements", flask.url_for("events")),
        Entry("Jeux", flask.url_for("games")),
        Entry(
            "Communauté",
            None,
            [
                Entry("Membres", flask.url_for("users")),
                Entry("Carte", flask.url_for("map")),
            ],
        ),
    ]
