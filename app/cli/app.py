from app import app, setup


@app.cli.command("setup")
def setup_():
    setup()
