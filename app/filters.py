from sssimp import filters

from app import app


@app.add_template_filter
def markdown(value: str):
    return filters.markdown(value)
