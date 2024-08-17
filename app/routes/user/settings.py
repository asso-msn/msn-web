import flask
from flask_login import current_user
from werkzeug.datastructures import FileStorage
from wtforms import (
    BooleanField,
    EmailField,
    FileField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)

from app import app
from app.db import User
from app.forms import Form, Length, LoginField, PasswordField
from app.services import audit, avatar
from app.services import user as service


def translate_image_type(image_type):
    if image_type == User.ImageType.local:
        return "Fichier"
    return image_type.capitalize().replace("_", " ")


class EditProfileForm(Form):
    login = LoginField()
    display_name = StringField(validators=[Length(max=30)])
    email = EmailField()
    bio = TextAreaField(validators=[Length(max=1000)])
    image = FileField()
    image_type = SelectField(
        choices=[(x, translate_image_type(x)) for x in User.ImageType]
    )
    hide_in_list = BooleanField()
    save = SubmitField()
    logout = SubmitField()
    unlink_discord = SubmitField()


@app.route("/settings/")
@service.authenticated
def settings():
    form = EditProfileForm()

    if form.logout.data or form.unlink_discord.data:
        form._csrf.validate_csrf_token(form, form.csrf_token)

    if form.logout.data:
        service.logout()
        flask.flash("Tu as été déconnecté")
        return app.redirect("index")

    if form.unlink_discord.data:
        if not current_user.password:
            flask.flash(
                "Tu dois définir un mot de passe pour déconnecter ton compte de"
                " Discord",
                "error",
            )
            return app.redirect("settings")

        with app.session() as s:
            user = s.query(User).get(current_user.id)
            user.discord_id = None
            user.discord_access_token = None
            user.discord_refresh_token = None
            if user.image_type == User.ImageType.discord:
                user.reset_avatar()
            s.commit()
            audit.log("Discord unlinked", user=user)
        flask.flash("Ton compte Discord a été retiré")
        return app.redirect("settings")

    if not form.validate_on_submit():
        form.login.data = form.login.data or current_user.login
        form.display_name.data = (
            form.display_name.data or current_user.display_name
        )
        form.email.data = form.email.data or current_user.email
        form.bio.data = form.bio.data or current_user.bio
        form.image_type.data = form.image_type.data or current_user.image_type
        form.hide_in_list.data = (
            form.hide_in_list.data or current_user.hide_in_list
        )

        if not current_user.email:
            form.image_type.choices = [
                x
                for x in form.image_type.choices
                if x[0] != User.ImageType.gravatar
            ]

        if not current_user.discord_access_token:
            form.image_type.choices = [
                x
                for x in form.image_type.choices
                if x[0] != User.ImageType.discord
            ]

        return app.render("users/settings", form=form, title="Paramètres")

    with app.session() as s:
        need_avatar_refresh = False
        changed_avatar_type = False
        user = s.query(User).get(current_user.id)

        user.login = form.login.data
        user.display_name = form.display_name.data
        user.bio = form.bio.data
        user.hide_in_list = form.hide_in_list.data

        if user.image_type != form.image_type.data:
            user.image_type = form.image_type.data
            changed_avatar_type = True

        if user.image_type != User.ImageType.local:
            del form.image
            if changed_avatar_type:
                need_avatar_refresh = True

        if user.image_type == User.ImageType.local:
            if not form.image.data:
                user.image = None
            else:
                image: FileStorage = form.image.data
                try:
                    image = avatar.convert(image)
                except ValueError:
                    flask.flash("Format d'image non supporté", "error")
                    return app.redirect("settings")
                image_hash = avatar.save(image)
                if (
                    not changed_avatar_type
                    and user.image
                    and (
                        s.query(User)
                        .filter(
                            User.image == user.image,
                            User.id != user.id,
                        )
                        .count()
                    )
                    == 0
                ):
                    avatar.delete(user.image)
                user.image = image_hash

        if (
            user.email != form.email.data
            and user.image_type == User.ImageType.gravatar
        ):
            need_avatar_refresh = True
        user.email = form.email.data

        if need_avatar_refresh:
            user.refresh_avatar()

        s.commit()
        flask.flash("Profil mis à jour")
    return app.redirect("settings")


class PasswordForm(Form):
    password = PasswordField()
    delete = SubmitField()


@app.route("/settings/password/")
@service.authenticated
def settings_password():
    form = PasswordForm()

    if form.delete.data:
        del form.password
        if form.validate_on_submit():
            if not current_user.has_discord:
                flask.flash(
                    "Ton compte doit être lié à Discord pour pouvoir supprimer"
                    " l'authentification par mot de passe",
                    "error",
                )
                return app.redirect("settings_password")

            with app.session() as s:
                user = s.query(User).get(current_user.id)
                user.password = None
                s.commit()
                audit.log("Password deleted", user=user)
            flask.flash("Mot de passe supprimé")
            return app.redirect("settings")

    if not form.validate_on_submit():
        return app.render(
            "users/password", form=form, title="Mot de passe", page="password"
        )

    with app.session() as s:
        user = s.query(User).get(current_user.id)
        service.set_password(user, form.password.data)
        s.commit()
        audit.log("Password changed", user=user)
    flask.flash("Mot de passe mis à jour")
    return app.redirect("settings")
