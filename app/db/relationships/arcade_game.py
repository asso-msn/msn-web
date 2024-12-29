from __future__ import annotations

from typing import TYPE_CHECKING

from .. import Column, ForeignKey, Table, column, relation

if TYPE_CHECKING:
    from .. import Arcade, Game


class ArcadeGame(Table):
    arcade_slug = column(ForeignKey("arcades.slug"), primary_key=True)
    game_id = column(ForeignKey("games.id"), primary_key=True)
    version: Column[str]

    arcade: Column[Arcade] = relation("Arcade", back_populates="games")
    game: Column[Game] = relation("Game", back_populates="arcades")
