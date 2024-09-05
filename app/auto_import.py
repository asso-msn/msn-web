import importlib
import logging
from pathlib import Path

from app import ROOT_DIR


def _import_file(file: Path):
    file = file.relative_to(ROOT_DIR.parent)
    module = ".".join(file.with_suffix("").parts)
    logging.debug(f"Auto loading module `{module}`")
    importlib.import_module(module)


def auto_import(path: str | Path):
    """Recursively import modules at `path` relative to `app.ROOT_DIR`."""
    logging.debug(f"Looking for modules in `{path}`")
    path = ROOT_DIR / path
    if path.with_suffix(".py").is_file():
        _import_file(path)
        return
    for file in path.rglob("*.py"):
        if file.stem in ("__init__", "env"):
            continue
        _import_file(file)
