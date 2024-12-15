import click

from app import app


@app.cli.command("setup")
def setup_():
    app.setup()


@app.cli.command("tasks")
@click.argument("task", default="")
def tasks(task):
    from app import tasks

    tasks.run_all(task)
