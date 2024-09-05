from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey

from .. import Column, Table, column, relation

if TYPE_CHECKING:
    from .. import Game, User


class UserGame(Table):
    user_id = column(ForeignKey("users.id"), primary_key=True)
    game_id = column(ForeignKey("games.id"), primary_key=True)
    favorite: Column[bool] = column(default=False)

    user: Column[User] = relation("User", back_populates="games")
    game: Column[Game] = relation("Game", back_populates="users")
