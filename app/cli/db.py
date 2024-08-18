from app import app, db


@app.cli.group("db")
def group():
    pass


@group.command()
def create():
    db.create_all()
