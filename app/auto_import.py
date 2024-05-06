import importlib
import logging

from app import ROOT_DIR


def auto_import(path: str):
    """Automagically imports all Python modules in a given directory."""
    path = ROOT_DIR / path
    for file in path.rglob("*.py"):
        if file.stem == "__init__":
            continue
        file = file.relative_to(ROOT_DIR.parent)
        module = ".".join(file.with_suffix("").parts)
        logging.info(f"Auto loaded module `{module}`")
        importlib.import_module(module)
