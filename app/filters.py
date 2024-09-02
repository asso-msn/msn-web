from datetime import datetime

from arrow import Arrow
from sssimp import filters

from app import app, config


@app.add_template_filter
def markdown(value: str):
    return filters.markdown(value)


@app.add_template_filter
def humanize(value: datetime):
    arrow = Arrow.fromdatetime(value)
    return arrow.humanize(locale=config.LANG)


@app.add_template_filter
def arrow(value: datetime):
    return Arrow.fromdatetime(value)


@app.add_template_filter
def slugify(value: str):
    return value.replace(" ", "-").lower()
