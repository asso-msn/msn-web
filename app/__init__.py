import logging
import os
from logging import Formatter
from pathlib import Path

import flask
import werkzeug.utils
from flask_assets import Bundle, Environment
from flask_login import LoginManager

ROOT_DIR = Path(__file__).parent
VAR_DIR = Path("var")

from app import db  # noqa: E402
from app.auto_import import auto_import  # noqa: E402

from . import data  # noqa: E402


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

        self.login_manager = LoginManager(self)

        VAR_DIR.mkdir(exist_ok=True)
        secret_key_path = VAR_DIR / "secret_key.txt"
        if not secret_key_path.exists():
            secret_key_path.write_text(os.urandom(24).hex())
        self.config["SECRET_KEY"] = secret_key_path.read_text().strip()

        db.create_all()

    def redirect(self, route, code=302):
        url = flask.url_for(route)
        return werkzeug.utils.redirect(url, code)

    def render(self, template_name, **context):
        context.setdefault("page", template_name)
        return flask.render_template(f"{template_name}.html.j2", **context)

    def session(self, **kwargs):
        return db.session(**kwargs)

    def route(self, rule, **options):
        """
        Using @app.route instead of @app.<method> defaults to accepting both GET
        and POST methods, useful for form-based routes.
        """
        options.setdefault("methods", ("GET", "POST"))
        return super().route(rule, **options)


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


for module in ("cli", "filters", "routes"):
    auto_import(module)
