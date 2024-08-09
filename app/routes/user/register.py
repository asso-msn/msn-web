from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField

from app import app
from app.forms import (
    AlnumPlusValidator,
    DataRequired,
    Length,
    LoginTakenValidator,
    NotReservedNameValidator,
)
from app.services import user as service


class RegisterForm(FlaskForm):
    login = StringField(
        validators=[
            DataRequired(),
            AlnumPlusValidator(),
            NotReservedNameValidator(),
            LoginTakenValidator(),
        ],
    )
    password = PasswordField(
        validators=[
            DataRequired(),
            Length(min=4),
        ],
    )


@app.route("/register/")
def register():
    form = RegisterForm()
    if not form.validate_on_submit():
        return app.render("user/register", form=form)
    service.register(form.login.data, form.password.data)
    return app.redirect("index")
