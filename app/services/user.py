from datetime import UTC, datetime

import flask_login
import sqlalchemy as sa
import werkzeug.security
from flask_login import current_user

from app import app
from app.db import User


@app.login_manager.user_loader
def user_loader(id) -> User:
    with app.session() as s:
        return s.query(User).get(id)


@app.before_request
def update_last_seen():
    if not current_user.is_authenticated:
        return
    with app.session() as s:
        user = s.query(User).get(current_user.id)
        user.last_seen = datetime.now(UTC)
        s.commit()


def login(user: User) -> User:
    flask_login.login_user(user, remember=True)
    return user


def get_by_login(login_: str) -> User:
    login_ = login_.strip().lower()
    with app.session() as s:
        return s.query(User).filter(sa.func.lower(User.login) == login_).first()


def check_login(login_: str, password: str) -> User:
    user = get_by_login(login_)
    if user is None:
        return None
    if not werkzeug.security.check_password_hash(user.password, password):
        return None
    login(user)
    return user


def register(login_: str, password: str) -> User:
    with app.session() as s:
        user = User(login=login_)
        set_password(user, password)
        s.add(user)
        s.commit()
        login(user)
        return user


def hash(password: str) -> str:
    return werkzeug.security.generate_password_hash(password)


def set_password(user: User, password: str):
    user.password = hash(password)


def logout():
    flask_login.logout_user()


authenticated = flask_login.login_required
