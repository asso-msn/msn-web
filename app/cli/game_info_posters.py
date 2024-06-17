from pathlib import Path

import click

from app import app
from app.services import game_info_posters as service

OUTPUT_DIR = Path("output")


@app.cli.command("posters")
@click.argument("game_id", default="")
def game_info_posters(game_id):
    games = service.get_games_list()
    if game_id not in games:
        raise click.UsageError(
            f"Invalid game. Choose from: {', '.join(games)}."
        )
    game = service.get_game(game_id)
    OUTPUT_DIR.mkdir(exist_ok=True)
    dest = OUTPUT_DIR / f"{game_id}.pdf"
    service.save_pdf(game, dest)
    click.echo(f"Generated game info poster at `{dest}`.")
