import hashlib
from io import BytesIO
from pathlib import Path

from werkzeug.datastructures import FileStorage

from app import VAR_DIR, app, config
from app.db import User
from app.services import audit, discord

try:
    from wand.exceptions import MissingDelegateError
    from wand.image import Image
except ImportError as e:
    wand_import_error = e
    Image = None

AVATARS_DIR = VAR_DIR / "avatars"


class UnsupportedImageFormat(Exception):
    pass


def convert(image: FileStorage) -> BytesIO:
    """
    Creates a streamable BytesIO object of a WebP from an image file provided
    by a form upload.
    """

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
    """Avatar hash to real path"""

    return AVATARS_DIR / f"{hash}.webp"


def get_avatar_hash(image: BytesIO) -> str:
    """Get hash from a streamable BytesIO object"""

    result = hashlib.md5(image.read()).hexdigest()
    image.seek(0)
    return result


def reset(user: User):
    user.image = None
    user.image_type = User.ImageType.empty


def set_gravatar(user: User):
    if not user.email:
        reset(user)
        return
    email = user.email.lower()
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    size = config.GRAVATAR_AVATAR_SIZE
    image = f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=mp"
    if user.image == image:
        return
    user.image = image
    user.image_type = User.ImageType.gravatar
    audit.log("Gravatar avatar set", user=user)


def save(image: BytesIO) -> str:
    """Saves streamable BytesIO object to disk"""

    AVATARS_DIR.mkdir(exist_ok=True)
    hash = get_avatar_hash(image)
    path = get_avatar_path(hash)
    if not path.exists():
        with path.open("wb") as f:
            size = f.write(image.read())
        audit.log(
            "Local avatar saved",
            hash=hash,
            size_mb=size / 1024 / 1024,
        )
    return hash


def delete(hash: str):
    """Deletes avatar from disk from its hash"""

    path = get_avatar_path(hash)
    if path.exists():
        path.unlink()
        audit.log("Local avatar deleted", hash=hash)


def delete_if_unused(hash: str):
    """Deletes avatar from disk if it's not used by any user"""

    with app.session() as s:
        if not s.query(User).filter_by(image=hash).count():
            delete(hash)
            audit.log("Unused local avatar deleted", hash=hash)


def update(user: User, type: User.ImageType, image: FileStorage = None) -> bool:
    """Update user avatar"""

    previous_image = user.image
    previous_type = user.image_type

    if type == User.ImageType.local and image:
        try:
            image = convert(image)
        except ValueError as e:
            raise UnsupportedImageFormat from e
        user.image = save(image)
        user.image_type = User.ImageType.local

    if type == User.ImageType.gravatar:
        set_gravatar(user)

    if type == User.ImageType.discord and type != previous_type:
        discord.set_avatar(user)

    if type == User.ImageType.empty or not user.image:
        reset(user)

    if previous_type == User.ImageType.local and (previous_image != user.image):
        delete_if_unused(previous_image)

    if previous_type != user.image_type or previous_image != user.image:
        audit.log(
            "Avatar updated",
            user=user,
            previous_image=previous_image,
            previous_type=previous_type,
            new_image=user.image,
            new_type=user.image_type,
        )
        return True
    return False
