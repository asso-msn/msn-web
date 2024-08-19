import functools
from pathlib import Path

import ruamel.yaml
import sssimp.generators.data
from sssimp.generators.markdown import markdown_to_html

yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def resolve(path: str):
    return Path("data") / path


@functools.cache
def load(path: str, flat=False) -> dict:
    """
    Load data from a path in the data directory.
    Use flat=True to get a single level dictionary instead of one that mirrors
    the directory structure.
    """
    path = resolve(path)
    return sssimp.generators.data.get(path, flat=flat)


@functools.cache
def markdown(path: str):
    path = resolve(path).with_suffix(".md")
    return markdown_to_html(path.read_text())
