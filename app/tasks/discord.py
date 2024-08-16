from app import app
from app.services import discord as service


@app.scheduler.task("interval", days=1)
def refresh_tokens():
    service.refresh_tokens()


@app.scheduler.task("interval", minutes=10)
def refresh_avatars():
    service.refresh_avatars()
