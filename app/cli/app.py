from app import app


@app.cli.command("setup")
def setup_():
    app.setup()


@app.cli.command("tasks")
def tasks():
    from app import tasks

    tasks.run_all()
