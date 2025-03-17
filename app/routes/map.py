from dataclasses import dataclass

import flask

from app import app
from app.db import User
from app.services import user


@dataclass
class UserPoint:
    latitude: float
    longitude: float
    map_point: str
    map_point_id: int
    name: str
    icon: str
    link: str


@app.get("/map/")
def map():
    with app.session() as s:
        query = s.query(User)
        user.filter_public(query)
        query = query.filter(User.map_point_id.isnot(None))
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
    return app.render(
        "map", user_points=user_points, title="La carte des membres"
    )
