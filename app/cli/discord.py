import click

from app import app, config
from app.services import discord as service
from app.services import games


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


@discord.command("import")
def import_games():
    """Import Discord members game roles to games lists"""
    users = service.import_games_lists()
    if not users:
        print("No change.")
        return
    print("Refreshed games for:", users)


@discord.command()
def create():
    """Create Discord roles using games data files"""
    api = service.API(config.DISCORD_BOT_TOKEN)
    server = api.get_server()
    games_ = games.get_all()
    roles_to_create = [x.name for x in games_ if not server.get_role(x.name)]

    print("Will create Discord roles:", roles_to_create)
    if not click.confirm("Continue?"):
        return

    for name in roles_to_create:
        api.create_role(server.id, name=name)
        print("Created role", name)
