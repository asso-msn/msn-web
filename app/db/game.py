from __future__ import annotations

from typing import TYPE_CHECKING

from app.repr import auto_repr

from . import Column, Id, Table, column, relation

if TYPE_CHECKING:
    from . import Arcade, User


@auto_repr("slug")
class Game(Table, Id):
    slug: Column[str] = column(unique=True)

    users: Column[list[User]] = relation(
        "UserGame", back_populates="game", cascade="all, delete-orphan"
    )
    arcades: Column[list[Arcade]] = relation(
        "ArcadeGame", back_populates="game", cascade="all, delete-orphan"
    )

    @property
    def data(self):
        from app import app

        games = app.data.get("games")
        if not games or not (game := games.get(self.slug)):
            raise ValueError(f"Game {self.slug} not found in data files")
        return game
