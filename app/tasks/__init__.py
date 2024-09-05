from app import app


def run_all():
    for job in app.scheduler.get_jobs():
        app.scheduler.run_job(job.id)
