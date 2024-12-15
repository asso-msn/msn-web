import functools
import time
from datetime import datetime

from app import app
from app.services import audit


def run_all():
    for job in app.scheduler.get_jobs():
        app.scheduler.run_job(job.id)


def descript_task(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        audit.log(f"Task started: {f.__name__}", start=datetime.now())
        f(*args, **kwargs)
        delta = time.monotonic() - start
        minutes, seconds = int(delta // 60), int(delta % 60)
        duration = f"{minutes}m {seconds}s"
        audit.log(f"Task finished: {f.__name__}", duration=duration)

    return wrapper
