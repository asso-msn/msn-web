from app import app
from app.services import games as service


@app.route("/games/")
def games():
    return service.get_games()
