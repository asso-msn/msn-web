import logging
import os
from logging import Formatter
from pathlib import Path

ROOT_DIR = Path(__file__).parent

import flask

from app.auto_import import auto_import


class App(flask.Flask):
    def __init__(self):
        super().__init__(__name__)

        @self.context_processor
        def add_self():
            return {"app": self}

    def render(self, template_name_or_list, **context):
        return flask.render_template(
            f"{template_name_or_list}.html.j2", **context
        )


format = "[%(levelname)s] %(name)s - %(pathname)s:%(lineno)s: %(message)s"


class CustomFormatter(Formatter):
    def format(self, record):
        # Replace the pathname with a path relative to the current working directory
        # This allows for easy navigation to the file from an IDE
        record.pathname = os.path.relpath(record.pathname)
        return super().format(record)


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter(format))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler],
)


app = App()

auto_import("pages")
logging.debug(app.url_map)
