from app import app, db
from app.services import games


@app.cli.group("db")
def group():
    pass


@group.command()
def create():
    db.create_all()
    games.populate()
