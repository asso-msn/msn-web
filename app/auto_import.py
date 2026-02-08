import importlib
from pathlib import Path

from app import ROOT_DIR, logger


def _import_file(file: Path, excludes: list[str] | None = None):
    file = file.relative_to(ROOT_DIR.parent)
    module = ".".join(file.with_suffix("").parts)
    if excludes and any(module.startswith(exclude) for exclude in excludes):
        logger.debug(f"Skipping module `{module}` matching exclude patterns")
        return
    logger.debug(f"Auto loading module `{module}`")
    importlib.import_module(module)


def auto_import(path: str | Path, excludes: list[str] | None = None):
    """Recursively import modules at `path` relative to `app.ROOT_DIR`."""
    logger.debug(f"Looking for modules in `{path}`")
    path = ROOT_DIR / path
    if path.with_suffix(".py").is_file():
        _import_file(path)
        return
    for file in path.rglob("*.py"):
        if file.stem in ("__init__",):
            continue
        _import_file(file, excludes=excludes)
