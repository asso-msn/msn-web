from app import app
from app.services import audit
from app.services import discord as service
from app.tasks import descript_task


@app.scheduler.task("interval", days=1)
@descript_task
def refresh_tokens():
    users = service.refresh_tokens()
    if users:
        audit.log("Task refreshed Discord tokens", users=users)


@app.scheduler.task("interval", minutes=10)
@descript_task
def refresh_avatars():
    users = service.refresh_avatars()
    if users:
        audit.log("Task refreshed Discord avatars", users=users)


@app.scheduler.task("interval", hours=1)
@descript_task
def import_games_lists():
    users = service.import_games_lists()
    if users:
        audit.log("Task imported Discord games lists", users=users)
