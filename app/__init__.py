import sys

if sys.version_info < (3, 11):
    raise RuntimeError("Python 3.11+ is required")
import dataclasses
import logging
import os
import secrets
from pathlib import Path

import flask
import werkzeug.utils
from flask_apscheduler import APScheduler
from flask_assets import Bundle, Environment
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel as Model

from app.services.config import Config

config = Config()
ROOT_DIR = Path(__file__).parent.resolve()
VAR_DIR = Path("var").resolve()

from app import db  # noqa: E402

from . import auto_import, data  # noqa: E402


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
                "css/events.css",
                "css/forms.css",
                "css/user.css",
                "css/responsive.css",
                output="style.css",
            ),
        )
        self.assets.register(
            "js", Bundle("js/flash.js", "js/forms.js", output="script.js")
        )

        # OAuth dance does not work with SameSite=Srict
        self.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        self.config["USE_SESSION_FOR_NEXT"] = True
        self.login_manager = LoginManager(self)
        self.login_manager.login_view = "login"
        self.login_manager.login_message = (
            "Tu dois te connecter pour accéder à cette page."
        )

        self.scheduler = APScheduler(app=self)

        VAR_DIR.mkdir(exist_ok=True)

        # Flask-SQLAlchemy is only used for the session backend. Codebase uses
        # self-managed SQLAlchemy for the database.
        self.config["SQLALCHEMY_DATABASE_URI"] = db.URI
        FlaskSQLAlchemy = SQLAlchemy(self)

        # self.config["SESSION_TYPE"] = "cachelib"
        # self.config["SESSION_CACHELIB"] = FileSystemCache(
        #     str(VAR_DIR / "flask_session"),
        # )
        self.config["SESSION_TYPE"] = "sqlalchemy"
        self.config["SESSION_SQLALCHEMY"] = FlaskSQLAlchemy
        self.config["SESSION_SERIALIZATION_FORMAT"] = "json"
        self.cache = Session(self)

        secret_key_path = VAR_DIR / "secret_key.txt"
        if not secret_key_path.exists():
            secret_key_path.write_text(secrets.token_hex())
        self.config["SECRET_KEY"] = secret_key_path.read_text().strip()

        self.scheduler.start()
        if self.debug:
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

        if dataclasses.is_dataclass(rv):
            rv = dataclasses.asdict(rv)

        return super().make_response(rv)


format = "[%(levelname)s] %(name)s - %(pathname)s:%(lineno)s: %(message)s"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Replace the pathname with a path relative to the current working
        # directory
        # This allows for easy navigation to the file from an IDE, usually using
        # Ctrl+Click
        record.pathname = os.path.relpath(record.pathname)
        return super().format(record)


class CustomFilter(logging.Filter):
    def filter(self, record):
        return record.name == "root"


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter(format))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addFilter(CustomFilter())

logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# TODO: Implement named logger in sssimp
# logging.getLogger("sssimp").setLevel(logging.WARNING)

app = App()

app.config.from_object(config)

if not app.debug:
    logger.setLevel(logging.INFO)

for module in ("cli", "filters", "routes", "services", "tasks", "db"):
    auto_import.auto_import(module)


def _populate():
    from app.services import games

    games.populate()
