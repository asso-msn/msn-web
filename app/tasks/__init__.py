import functools
import time

from app import app


def run_all(task=None):
    for job in app.scheduler.get_jobs():
        if task and job.name != task:
            print(f"Skipping {job.name} != {task}")
            continue
        app.scheduler.run_job(job.id)


def descript_task(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        print(f"Task started: {f.__name__}")
        f(*args, **kwargs)
        delta = time.monotonic() - start
        minutes, seconds = int(delta // 60), int(delta % 60)
        duration = f"{minutes}m {seconds}s"
        print(f"Task finished: {f.__name__}, {duration} elapsed")

    return wrapper
