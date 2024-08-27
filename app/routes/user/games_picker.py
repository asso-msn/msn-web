from dataclasses import dataclass

from flask import request
from flask_login import current_user

from app import app, db
from app.db import User, UserGame
from app.services import audit, discord, games
from app.services import user as service


@app.route("/settings/games/")
@service.authenticated
def games_picker():
    games_ = games.get_all(sort="name")
    popular_games = games.get_popular(limit=10, sort="name")
    with app.session() as s:
        user = s.query(User).get(current_user.id)
        return app.render(
            "users/games_picker",
            games=games_,
            popular_games=popular_games,
            user=user,
        )


@dataclass
class GamePickerResponse:
    modified: bool


@app.post("/api/settings/games/<slug>")
@service.authenticated
def api_games_picker_post(slug: str):
    game = games.get(slug)
    with app.session() as s:
        action = db.greate(
            s,
            UserGame,
            filter={"user_id": current_user.id, "game_id": game.db.id},
        )
        s.commit()
        audit.log(f"Game {game} added to {current_user}")
    discord.add_game(current_user, game)
    return GamePickerResponse(modified=action.created)


@app.delete("/api/settings/games/<slug>")
@service.authenticated
def api_games_picker_delete(slug: str):
    game = games.get(slug)
    with app.session() as s:
        query = s.query(UserGame).filter_by(
            user_id=current_user.id, game_id=game.db.id
        )
        exists = bool(query.first())
        result = GamePickerResponse(modified=exists)
        if exists:
            query.delete()
        s.commit()
        audit.log(f"Game {game} removed to {current_user}")
    discord.remove_game(current_user, game)
    return result


@app.patch("/api/settings/games/<slug>")
@service.authenticated
async def api_games_picker_patch(slug: str):
    favorite = request.json.get("favorite")
    game = games.get(slug)
    with app.session() as s:
        instance = (
            s.query(UserGame)
            .filter_by(user_id=current_user.id, game_id=game.db.id)
            .first()
        )
        result = GamePickerResponse(modified=instance.favorite != favorite)
        instance.favorite = favorite
        s.commit()
        audit.log(f"Game {game} favorite set to {favorite} for {current_user}")
    return result
