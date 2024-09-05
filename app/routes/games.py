import flask
import sqlalchemy.orm as sa_orm
from wtforms import SelectField, StringField

from app import app
from app.db import Game
from app.forms import Form
from app.services import games as service


class SearchForm(Form):
    name = StringField()
    platform = SelectField(
        choices=[("all", "Tous"), ("", "-----")]
        + [(p, p) for p in service.get_platforms()]
    )


@app.route("/games/")
def games():
    form = SearchForm(flask.request.args)
    form.platform.data = form.platform.data or "Arcade"
    games_ = service.get_all(sort="name")
    for game in games_:
        game.load_db(sa_orm.joinedload(Game.users))
    return app.render("games", games=games_, title="Les jeux", form=form)


@app.route("/games/<slug>/")
def game(slug):
    flask.flash("TODO!")
    return app.redirect("games")
