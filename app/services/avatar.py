import hashlib
from io import BytesIO
from pathlib import Path

from werkzeug.datastructures import FileStorage

from app import VAR_DIR, config

try:
    from wand.exceptions import MissingDelegateError
    from wand.image import Image
except ImportError as e:
    wand_import_error = e
    Image = None

AVATARS_DIR = VAR_DIR / "avatars"


def convert(image: FileStorage) -> BytesIO:
    if Image is None:
        raise ImportError(
            "Wand is not installed. See documentation:"
            " https://docs.wand-py.org/en/latest/guide/install.html"
        ) from wand_import_error

    stream = BytesIO()
    try:
        with Image(file=image) as img:
            size = config.AVATAR_SIZE
            img.format = "webp"
            img.resize(size, size)
            img.save(file=stream)
    except MissingDelegateError as e:
        raise ValueError("Unsupported image format") from e
    stream.seek(0)
    return stream


def get_avatar_path(hash: str) -> Path:
    return AVATARS_DIR / f"{hash}.webp"


def get_avatar_hash(image: BytesIO) -> str:
    result = hashlib.md5(image.read()).hexdigest()
    image.seek(0)
    return result


def save(image: BytesIO) -> str:
    AVATARS_DIR.mkdir(exist_ok=True)
    hash = get_avatar_hash(image)
    path = get_avatar_path(hash)
    if not path.exists():
        with path.open("wb") as f:
            f.write(image.read())
    return hash


def delete(hash: str):
    path = get_avatar_path(hash)
    if path.exists():
        path.unlink()
