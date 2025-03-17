import flask

from app import app
from app.db import User


@app.get("/users/<login>/")
def user(login: str):
    with app.session() as s:
        user = s.query(User).filter_by(login=login).first()
        if not user:
            return flask.abort(404)
        return app.render(
            "users/profile",
            user=user,
            title=f"Profil MSN de {user}",
            embed_image=user.avatar_url,
        )
