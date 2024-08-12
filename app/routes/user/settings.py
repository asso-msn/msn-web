import flask
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import EmailField, FileField, SelectField, StringField

from app import app
from app.db import User
from app.forms import Length, LoginField, PasswordField
from app.services import user as service


def translate_image_type(image_type):
    if image_type == User.ImageType.local:
        return "Fichier"
    return image_type.capitalize().replace("_", " ")


class EditProfileForm(FlaskForm):
    login = LoginField()
    display_name = StringField(validators=[Length(max=32)])
    email = EmailField()
    password = PasswordField()
    bio = StringField(validators=[Length(max=1000)])
    image = FileField()
    image_type = SelectField(
        choices=[(x, translate_image_type(x)) for x in User.ImageType]
    )


class LogoutForm(FlaskForm):
    pass


@app.route("/settings/")
@service.authenticated
def settings():
    form = EditProfileForm()
    logout = LogoutForm()

    if logout.validate_on_submit():
        service.logout()
        flask.flash("Tu as été déconnecté")
        return app.redirect("index")

    form.login.data = current_user.login

    return app.render("user/settings", form=form, logout=logout)
