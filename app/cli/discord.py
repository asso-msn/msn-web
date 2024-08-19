import click

from app import app
from app.services import discord as service


@app.cli.group()
def discord():
    pass


@discord.command()
@click.argument("login", default="")
def token(login):
    """Refresh Discord access tokens"""
    users = service.refresh_tokens(login=login)
    if not users:
        print("No change.")
        return
    print("Refreshed token for:", users)


@discord.command()
@click.argument("login", default="")
def avatar(login):
    """Refresh Discord avatar URLs"""
    users = service.refresh_avatars(login=login)
    if not users:
        print("No change.")
        return
    print("Refreshed avatar for:", users)
