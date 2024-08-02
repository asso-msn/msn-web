import flask
from flask_wtf import FlaskForm

from app import app, db
from app.db import User
from app.services import user as service


class LogoutForm(FlaskForm):
    pass


@service.authenticated
@app.route("/settings/")
def settings():
    logout = LogoutForm()
    if logout.validate_on_submit():
        service.logout()
        flask.flash("Vous avez été déconnecté")
        return app.redirect("index")
    return app.render("user/settings", logout=logout)
