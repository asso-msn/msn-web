from pathlib import Path

import yaml
from sssimp.generators.markdown import markdown_to_html


def resolve(path: str):
    return Path("data") / path


def load(path: str):
    path = resolve(path)
    result = {}
    for file in path.rglob("*.yml"):
        result[file.stem] = yaml.safe_load(file.read_text())
    return result


def markdown(path: str):
    path = resolve(path).with_suffix(".md")
    return markdown_to_html(path.read_text())
