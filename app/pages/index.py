import flask

from app import app


@app.route("/")
def index():
    return flask.redirect(flask.url_for("events"))
