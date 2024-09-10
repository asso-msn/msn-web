import random
from dataclasses import dataclass

import flask

from app import app
from app.db import User


@dataclass
class UserPoint:
    lat: float
    lon: float
    name: str
    login: str
    icon: str
    link: str


@app.get("/map/")
def map():
    with app.session() as s:
        users = s.query(User).all()
        user_points = [
            UserPoint(
                lat=random.uniform(43, 50),
                lon=random.uniform(-1.5, 6.7),
                name=user.name,
                login=user.login,
                icon=user.avatar_url,
                link=flask.url_for("user", login=user.login),
            )
            for user in users
        ]
    return app.render("map", user_points=user_points)
