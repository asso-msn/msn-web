import sys

if sys.version_info < (3, 11):
    raise RuntimeError("Python 3.11+ is required")
import dataclasses
import logging
import os
import secrets
import urllib.parse
from pathlib import Path

import inspect
from flask import Flask, request, url_for, render_template
import werkzeug.utils
from flask_apscheduler import APScheduler
from flask_assets import Bundle, Environment
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from pydantic import BaseModel as Model

from app.services.config import Config

config = Config.load()
ROOT_DIR = Path(__file__).parent.resolve()
VAR_DIR = Path("var").resolve()

from app import db  # noqa: E402
from app.services import hier  # noqa: E402

from . import auto_import, data  # noqa: E402


class App(Flask):
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
                "hier": hier.get(),
            }

        @self.before_request
        def _():
            without_empty = {
                key: value for key, value in request.args.items() if value
            }
            if without_empty != dict(request.args):
                return self.redirect(
                    request.path + "?" + urllib.parse.urlencode(without_empty)
                )

        self.jinja_env.lstrip_blocks = True
        self.jinja_env.trim_blocks = True

        self.assets = Environment(self)
        self.assets.register(
            "css",
            Bundle(
                "css/base.css",
                "css/navbar.css",
                "css/events.css",
                "css/forms.css",
                "css/user.css",
                "css/responsive.css",
                output="style.css",
            ),
        )
        self.assets.register(
            "js",
            Bundle(
                "js/base.js",
                "js/navbar.js",
                "js/flash.js",
                "js/forms.js",
                "js/user.js",
                output="script.js",
            ),
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
        self.config["SESSION_USE_SIGNER"] = True
        self.config["SESSION_TYPE"] = "sqlalchemy"
        self.config["SESSION_SQLALCHEMY"] = FlaskSQLAlchemy
        self.config["SESSION_SERIALIZATION_FORMAT"] = "json"
        self.cache = Session(self)

        secret_key_path = VAR_DIR / "secret_key.txt"
        if not secret_key_path.exists():
            secret_key_path.write_text(secrets.token_hex())
        self.config["SECRET_KEY"] = secret_key_path.read_text().strip()

        if config.RUN_TASKS:
            self.scheduler.start()

    def redirect(self, route, external=False, code=302):
        external = external or route.split(":")[0] in ("http", "https")
        if not external and not route.startswith("/"):
            route = url_for(route)
        return werkzeug.utils.redirect(route, code)

    def render(self, template_name, **context):
        default_page = template_name
        default_og_data = {
            "image": url_for(
                "static", _external=True, filename="logo-border.png"
            ),
            "description": "Make Some Noise est une association \
            qui a pour but de promouvoir les jeux vidéo musicaux \
            sur bornes d'arcade, et les moyens d'y jouer chez soi.",
        }
        custom_og_data = context.get("og_data", default_og_data)
        merged_og_data = default_og_data | custom_og_data
        default_page = default_page.replace("/", "-")
        default_page = default_page.replace("_", "-")
        context.setdefault("page", default_page)
        context["og_data"] = merged_og_data
        return render_template(f"{template_name}.html.j2", **context)

    def session(self, **kwargs):
        return db.session(**kwargs)

    def route(self, rule, **options):
        """
        Using @app.route instead of @app.<method> defaults to accepting both GET
        and POST methods, useful for form-based routes.
        """
        options.setdefault("methods", ("GET", "POST"))

        def decorator(func):
            signature = inspect.signature(func)
            annotations = signature.parameters

            def wrapped_view(*args, **kwargs):
                for name, param in annotations.items():
                    if not issubclass(param.annotation, FlaskForm):
                        continue
                    form_class = param.annotation
                    # Choose data source based on HTTP method
                    if request.method == "POST":
                        form_data = request.form
                    else:
                        form_data = request.args
                    form_instance = form_class(form_data)
                    kwargs[name] = form_instance

                return func(*args, **kwargs)

            # Register the route with the wrapped view
            endpoint = options.pop("endpoint", func.__name__)
            self.add_url_rule(rule, endpoint, wrapped_view, **options)
            return wrapped_view

        return decorator

    def make_response(self, rv):
        if isinstance(rv, Model):
            rv = rv.model_dump()

        if dataclasses.is_dataclass(rv):
            rv = dataclasses.asdict(rv)

        return super().make_response(rv)

    def setup(self):
        """Populate the database with initial data"""
        from app.services import games, gps

        if self.debug:
            db.create_all()
        games.populate()
        gps.populate()


class CustomFormatter(logging.Formatter):
    def __init__(self):
        self._format = "[%(levelname)s] %(pathname)s:%(lineno)s: %(message)s"
        self._foreign_format = "[%(levelname)s] %(name)s: %(message)s"

    def format(self, record):
        # Replace the pathname with a path relative to the current working
        # directory
        # This allows for easy navigation to the file from an IDE, usually using
        # Ctrl+Click
        record.pathname = os.path.relpath(record.pathname)
        if record.name != "root":
            return logging.Formatter(self._foreign_format).format(record)
        return logging.Formatter(self._format).format(record)


class CustomFilter(logging.Filter):
    def filter(self, record):
        if record.name != "root":
            return False
        if "/".join(Path(record.pathname).parts).endswith(
            "sssimp/generators/data.py"
        ):
            return False
        return True


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addFilter(CustomFilter())

logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("tzlocal").setLevel(logging.WARNING)
# TODO: Implement named logger in sssimp
# logging.getLogger("sssimp").setLevel(logging.WARNING)

app = App()

app.config.from_object(config)

if not app.debug:
    logger.setLevel(logging.INFO)


for module in ("cli", "filters", "routes", "services", "tasks", "db"):
    auto_import.auto_import(module)

if app.debug:
    app.setup()

if config.RUN_TASKS:
    from app import tasks

    tasks.run_all()
