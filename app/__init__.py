import logging
import os
import secrets
from logging import Formatter
from pathlib import Path

import flask
import werkzeug.utils
from cachelib import SimpleCache
from flask_assets import Bundle, Environment
from flask_login import LoginManager
from flask_session import Session
from pydantic import BaseModel as Model

ROOT_DIR = Path(__file__).parent
VAR_DIR = Path("var")

from app import db  # noqa: E402
from app.auto_import import auto_import  # noqa: E402

from . import data  # noqa: E402


class App(flask.Flask):
    def __init__(self):
        super().__init__(__name__)

        self.data = data.load(".")
        if links := self.data.get("links"):
            if username := self.data["links"].get("instagram_username"):
                links["instagram"] = f"https://instagram.com/{username}"
            if username := self.data["links"].get("x_username"):
                links["x"] = f"https://x.com/{username}"

        @self.context_processor
        def _():
            return {
                "app": self,
                "data": self.data,
            }

        self.jinja_env.lstrip_blocks = True
        self.jinja_env.trim_blocks = True

        self.assets = Environment(self)
        self.assets.register(
            "css",
            Bundle(
                "css/base.css",
                "css/forms.css",
                "css/login.css",
                "css/events.css",
                "css/responsive.css",
                output="style.css",
            ),
        )

        self.config["USE_SESSION_FOR_NEXT"] = True
        self.login_manager = LoginManager(self)
        self.login_manager.login_view = "login"
        self.login_manager.login_message = (
            "Tu dois te connecter pour accéder à cette page."
        )

        self.config["SESSION_TYPE"] = "cachelib"
        self.config["SESSION_CACHELIB"] = SimpleCache()
        Session(self)

        VAR_DIR.mkdir(exist_ok=True)
        secret_key_path = VAR_DIR / "secret_key.txt"
        if not secret_key_path.exists():
            secret_key_path.write_text(secrets.token_hex())
        self.config["SECRET_KEY"] = secret_key_path.read_text().strip()

        db.create_all()

    def redirect(self, route, external=False, code=302):
        external = external or route.split(":")[0] in ("http", "https")
        if not external and not route.startswith("/"):
            route = flask.url_for(route)
        return werkzeug.utils.redirect(route, code)

    def render(self, template_name, **context):
        default_page = template_name
        default_page = default_page.replace("/", "-")
        default_page = default_page.replace("_", "-")
        context.setdefault("page", default_page)
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

    def make_response(self, rv):
        if isinstance(rv, Model):
            rv = rv.model_dump()

        return super().make_response(rv)


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

from app.services.config import Config  # noqa: E402

config = Config()

app.config.from_object(config)


for module in ("cli", "filters", "routes"):
    auto_import(module)
