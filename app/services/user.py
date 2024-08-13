import flask_login
import werkzeug.security

from app import app
from app.db import User


@app.login_manager.user_loader
def user_loader(id) -> User:
    with app.session() as s:
        return s.query(User).get(id)


def login(user: User) -> User:
    flask_login.login_user(user, remember=True)
    return user


def check_login(login_: str, password: str) -> User:
    with app.session() as s:
        user = s.query(User).filter_by(login=login_).first()
    if user is None:
        return None
    if not werkzeug.security.check_password_hash(user.password, password):
        return None
    login(user)
    return user


def register(login_: str, password: str) -> User:
    password = hash(password)
    with app.session() as s:
        user = User(login=login_, password=password)
        s.add(user)
        s.commit()
        login(user)
    return user


def hash(password: str) -> str:
    return werkzeug.security.generate_password_hash(password)


def logout():
    flask_login.logout_user()


authenticated = flask_login.login_required
