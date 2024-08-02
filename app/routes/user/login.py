import flask
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField

from app import app
from app.forms import AlnumPlusValidator, DataRequired, Length
from app.services import user as service


class LoginForm(FlaskForm):
    login = StringField(
        "Login",
        validators=[
            DataRequired(),
            AlnumPlusValidator(),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=4),
        ],
    )


@app.route("/login/")
def login():
    form = LoginForm()

    def get():
        return app.render("user/login", form=form)

    if not form.validate_on_submit():
        return get()
    if not service.check_login(form.login.data, form.password.data):
        flask.flash("Identifiant ou mot de passe incorrect", "error")
        return get()
    flask.flash("Vous êtes désormais connecté")
    return app.redirect("index")
