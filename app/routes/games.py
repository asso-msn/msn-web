import flask
import sqlalchemy.orm as sa_orm

from app import app
from app.db import Game
from app.services import games as service


@app.route("/games/")
def games():
    games_ = service.get_all("name")
    for game in games_:
        game.load_db(sa_orm.joinedload(Game.users))
    return app.render("games", games=games_)


@app.route("/games/<slug>/")
def game(slug):
    flask.flash("TODO!")
    return app.redirect("games")
