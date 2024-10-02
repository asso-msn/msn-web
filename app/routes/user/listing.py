import flask
from wtforms import SelectField, StringField

from app import app
from app.db import Game, User, UserGame
from app.forms import Form
from app.paging import Pager
from app.services import games
from app.services import user as service


class SearchForm(Form):
    name = StringField()
    game = SelectField(
        choices=[("", "Tous"), ("", "-----")]
        + [(x.slug, x.name) for x in games.get_all(sort="name")],
        default="all",
    )


@app.get("/users/")
def users():
    form = SearchForm(flask.request.args)

    if form.game.data == "all":
        form.game.data = None

    with app.session() as s:
        query = s.query(User)
        query = service.filter_public(query)
        if form.name.data:
            query = query.where(
                User.display_name.ilike(f"%{form.name.data}%")
                | User.login.ilike(f"%{form.name.data}%")
            )
        if form.game.data:
            game = s.query(Game).filter_by(slug=form.game.data).one()
            query = query.filter(User.games.any(UserGame.game_id == game.id))
        pager = Pager.get_from_request(query, per_page=20, total=query.count())
        return app.render(
            "users/listing", pager=pager, title="Membres", form=form
        )
