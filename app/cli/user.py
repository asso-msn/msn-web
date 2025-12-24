import click

from app import app
from app.db import User
from app.services import audit


@app.cli.group()
def users():
    pass


@users.command()
@click.option("--discord-id", is_flag=False)
def delete(discord_id):
    if not discord_id:
        raise Exception("Must supply a parameter")
    with app.session() as s:
        query = s.query(User)
        query = query.filter_by(discord_id=discord_id)
        for user in query:
            answer = input(
                f"Going to delete user {user} definitely. Continue? [y/N] "
            )
            if answer.lower() in ("y", "yes"):
                s.delete(user)
                s.commit()
                audit.log("Deleted user", user)
