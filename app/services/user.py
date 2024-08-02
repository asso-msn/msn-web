import flask_login
import werkzeug.security

from app import app
from app.db import User


@app.login_manager.user_loader
def user_loader(id) -> User:
    with app.session() as session:
        return session.query(User).get(id)


def login(user: User) -> User:
    flask_login.login_user(user)
    return user


def check_login(id: str, password: str) -> User:
    with app.session() as session:
        user = session.query(User).get(id)
    if user is None:
        return None
    if not werkzeug.security.check_password_hash(user.password, password):
        return None
    login(user)
    return user


def register(id: str, password: str) -> User:
    password = werkzeug.security.generate_password_hash(password)
    with app.session() as session:
        user = User(id=id, password=password)
        session.add(user)
        session.commit()
    login(user)
    return user


def logout():
    flask_login.logout_user()


authenticated = flask_login.login_required
