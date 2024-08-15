import logging
import traceback
from datetime import datetime

import flask
from flask_login import current_user
from werkzeug.exceptions import HTTPException

from app import app
from app.services import audit


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e

    trace = traceback.format_exc()
    audit.log(
        "Unhandled exception",
        exception=e,
        codeblock=trace,
        user=current_user,
        request=flask.request,
        view=flask.request and flask.request.endpoint,
        level=logging.ERROR,
        time=datetime.now(),
    )
    flask.flash(
        "Un crash est survenu."
        " Une alerte automatique a été envoyée à notre équipe."
        f' Détails: "{e}"',
        "error",
    )
    return app.redirect("index")


@app.errorhandler(404)
def handle_404(e):
    flask.flash("Page introuvable", "error")
    return app.redirect("index")
