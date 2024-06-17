import logging
import os
from logging import Formatter
from pathlib import Path

from flask_assets import Bundle, Environment

ROOT_DIR = Path(__file__).parent

import flask

from app.auto_import import auto_import

from . import data


class App(flask.Flask):
    def __init__(self):
        super().__init__(__name__)

        @self.context_processor
        def _():
            return {
                "app": self,
                "data": data.load("."),
            }

        self.jinja_env.lstrip_blocks = True
        self.jinja_env.trim_blocks = True

        self.assets = Environment(self)
        self.assets.register(
            "css",
            Bundle(
                "css/base.css",
                "css/events.css",
                "css/responsive.css",
                output="style.css",
            ),
        )

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


for module in ("cli", "pages", "filters"):
    auto_import(module)
