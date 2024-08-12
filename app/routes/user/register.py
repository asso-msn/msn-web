from flask_wtf import FlaskForm

from app import app
from app.forms import DataRequired, Length, LoginField, PasswordField
from app.services import user as service


class RegisterForm(FlaskForm):
    login = LoginField()
    password = PasswordField()


@app.route("/register/")
def register():
    form = RegisterForm()
    if not form.validate_on_submit():
        return app.render(
            "user/register", form=form, page="login", title="Inscription"
        )
    service.register(form.login.data, form.password.data)
    return app.redirect("index")
