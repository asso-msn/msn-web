from app import app
from app.services import events as service


@app.route("/events/")
def events():
    return app.render("events", events=service.get_events())
