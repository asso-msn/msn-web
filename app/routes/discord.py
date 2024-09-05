import secrets

import flask
from flask_login import current_user
from wtforms import BooleanField, StringField

from app import app
from app.db import User
from app.forms import (
    AlnumPlusValidator,
    DataRequired,
    Form,
    LoginTakenValidator,
    NotReservedNameValidator,
)
from app.services import audit, avatar
from app.services import discord as service
from app.services import user as user_service

ALREADY_LINKED_MESSAGE = "Tu as déjà lié ton compte Discord."


@app.get("/login/discord/")
def discord_login():
    state = secrets.token_hex(16)
    flask.session["discord_state"] = state
    url = service.get_authorization_url(state=state)
    return flask.redirect(url)


@app.get("/login/discord/callback")
def discord_callback():
    code = flask.request.args.get("code")
    state = flask.request.args.get("state")  # noqa F841
    if not state or state != flask.session.pop("discord_state", None):
        flask.flash("Token de sécurité OAuth 2.0 State invalide.", "error")
        return app.redirect("index")
    token = service.get_discord_token(code)
    user = service.get_db_user(token.access_token)
    if not user:
        flask.session["discord_access_token"] = token.access_token
        flask.session["discord_refresh_token"] = token.refresh_token
        if current_user.is_authenticated:
            return app.redirect("discord_link_confirm")
        return app.redirect("discord_register")
    with app.session() as s:
        user = s.query(User).get(user.id)
        user.discord_access_token = token.access_token
        user.discord_refresh_token = token.refresh_token
        s.commit()
        user_service.login(user)

    if next := flask.session.pop("next", None):
        return app.redirect(next)

    return app.redirect("index")


class DiscordRegisterForm(Form):
    login = StringField(
        validators=[
            DataRequired(),
            AlnumPlusValidator(),
            NotReservedNameValidator(),
            LoginTakenValidator(),
        ]
    )
    use_avatar = BooleanField()


@app.route("/register/discord/")
def discord_register():
    form = DiscordRegisterForm()

    access_token = flask.session.get("discord_access_token")
    refresh_token = flask.session.get("discord_refresh_token")

    if not access_token or not refresh_token:
        return app.redirect("register")

    api = service.API(flask.session["discord_access_token"])
    user = api.get_user()

    if not form.validate_on_submit():
        # This is the only special character allowed by Discord but not by us
        form.login.data = user.username.replace(".", "_")
        form.use_avatar.data = True
        return app.render(
            "users/discord_register",
            form=form,
            page="login",
            title="Inscription via Discord",
        )

    with app.session() as s:
        user = User(
            login=form.login.data,
            discord_id=user.id,
            discord_access_token=access_token,
            discord_refresh_token=refresh_token,
        )
        s.add(user)
        s.commit()
        audit.log("User creation from Discord", user=user)
        user_service.login(user)
        if form.use_avatar.data:
            avatar.update(user, User.ImageType.discord)
            s.commit()
        service.import_games_lists(user.login)

    if next := flask.session.pop("next", None):
        return app.redirect(next)

    return app.redirect("index")


class DiscordLinkForm(Form):
    pass


@app.route("/link/discord/")
@user_service.authenticated
def discord_link():
    if current_user.has_discord:
        flask.flash(ALREADY_LINKED_MESSAGE, "error")
        return app.redirect("index")

    return app.render(
        "users/discord_link",
        page="link",
        title="Lier Discord",
    )


@app.route("/link/discord/confirm/")
@user_service.authenticated
def discord_link_confirm():
    if current_user.has_discord:
        flask.flash(ALREADY_LINKED_MESSAGE, "error")
        return app.redirect("index")

    access_token = flask.session.get("discord_access_token")
    refresh_token = flask.session.get("discord_refresh_token")

    if not access_token or not refresh_token:
        return app.redirect("discord_login")

    api = service.API(access_token=access_token)
    discord_user = api.get_user()

    with app.session() as s:
        if s.query(User).filter_by(discord_id=discord_user.id).count():
            flask.flash(
                "Ce compte Discord est déjà lié à un compte MSN.", "error"
            )
            return app.redirect("index")

    form = DiscordLinkForm()

    if not form.validate_on_submit():
        return app.render(
            "users/discord_link_confirm",
            form=form,
            page="link",
            title="Lier Discord",
            discord_user=discord_user,
        )

    with app.session() as s:
        user = s.query(User).get(current_user.id)
        user.discord_id = discord_user.id
        user.discord_access_token = access_token
        user.discord_refresh_token = refresh_token
        s.commit()
        audit.log("Discord account linked", user=user)

    flask.flash("Ton compte Discord a été lié avec succès.")
    return app.redirect("settings")
