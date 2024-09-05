from app import app, setup


@app.cli.command("setup")
def setup_():
    setup()


@app.cli.command("tasks")
def tasks():
    from app import tasks

    tasks.run_all()
