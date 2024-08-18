import flask

from app import app
from app.services import avatar as service


@app.get("/avatars/<hash>.webp")
def avatar(hash: str):
    """
    Should be registered as a static file route in the web server.
    Serves from `VAR_DIR/avatars/`.
    """
    path = service.get_avatar_path(hash)
    return flask.send_file(path, "image/webp")
