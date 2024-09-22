from pathlib import Path

import click

from app import app, pdf
from app.services import games

OUTPUT_DIR = Path("output")


@app.cli.group(name="pdf")
def group():
    pass


@group.command()
@click.argument("slug", default="")
def poster(slug):
    """Generate a game info poster."""
    if not slug:
        games_ = [game for game in app.data["games_posters"]]
    else:
        games_ = [slug]
    for slug in games_:
        game = games.get(slug)
        if not game:
            raise click.UsageError(
                f"Invalid game. Choose from: {', '.join(games.get_slugs())}."
            )
        OUTPUT_DIR.mkdir(exist_ok=True)
        dest = OUTPUT_DIR / f"{slug}.pdf"
        html = app.render("pdf/game_info_poster", game=game)
        pdf.save_html(html, dest)
        click.echo(f"Generated game info poster at `{dest}`.")
