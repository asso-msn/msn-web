import flask
from flask_wtf import FlaskForm

from app import app
from app.services import user as service


class LogoutForm(FlaskForm):
    pass


@app.route("/settings/")
@service.authenticated
def settings():
    logout = LogoutForm()
    if logout.validate_on_submit():
        service.logout()
        flask.flash("Vous avez été déconnecté")
        return app.redirect("index")
    return app.render("user/settings", logout=logout)
