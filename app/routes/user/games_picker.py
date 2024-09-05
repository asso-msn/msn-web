from dataclasses import dataclass

from flask import request
from flask_login import current_user

from app import app
from app.db import User
from app.services import games
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
    return GamePickerResponse(modified=games.add_to_list(slug, current_user))


@app.delete("/api/settings/games/<slug>")
@service.authenticated
def api_games_picker_delete(slug: str):
    return GamePickerResponse(
        modified=games.remove_from_list(slug, current_user)
    )


@app.patch("/api/settings/games/<slug>")
@service.authenticated
def api_games_picker_patch(slug: str):
    return GamePickerResponse(
        modified=games.set_favorite(
            slug, current_user, favorite=request.json.get("favorite")
        )
    )
