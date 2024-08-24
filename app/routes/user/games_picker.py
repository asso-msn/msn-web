from flask_login import current_user

from app import app
from app.db import User
from app.services import games
from app.services import user as service


@app.route("/settings/games/")
@service.authenticated
def games_picker():
    with app.session() as s:
        user = s.query(User).get(current_user.id)
        return app.render(
            "users/games_picker", games=games.get_all(sort="name"), user=user
        )


@app.post("/settings/games/")
@service.authenticated
def update_games_list(slug: str, add: bool, favorite: bool = False):
    pass
