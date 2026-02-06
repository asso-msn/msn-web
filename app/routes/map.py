from dataclasses import dataclass

import flask
from wtforms import SelectField

from app import app
from app.db import User, UserGame
from app.forms import Form
from app.services import games, user


@dataclass
class UserPoint:
    latitude: float
    longitude: float
    map_point: str
    map_point_id: int
    name: str
    icon: str
    link: str


class MapForm(Form):
    game = SelectField(
        choices=[("", "Tous")] + [(x.slug, x.name) for x in games.get_all()]
    )


@app.get("/map/")
def map():
    game = flask.request.args.get("game")
    with app.session() as s:
        query = s.query(User)
        user.filter_public(query)
        query = query.filter(User.map_point_id.isnot(None))
        if game and (game := games.get(game)):
            query = query.filter(
                User.games.any(UserGame.game.has(slug=game.slug))
            )
        user_points = [
            UserPoint(
                latitude=user.map_point.latitude,
                longitude=user.map_point.longitude,
                map_point=user.map_point.name,
                map_point_id=user.map_point_id,
                name=user.name,
                icon=user.avatar_url,
                link=flask.url_for("user", login=user.login),
            )
            for user in query
        ]
    form = MapForm()
    if game:
        form.game.data = game.slug
    return app.render(
        "map", user_points=user_points, title="La carte des membres", form=form
    )
