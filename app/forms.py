from wtforms import ValidationError
from wtforms.validators import DataRequired, Length

from app import db
from app.db import User


class DataRequired(DataRequired):
    def __init__(self, message="Ce champ est obligatoire"):
        self.message = message


class Length(Length):
    def __init__(self, min=-1, max=-1, message=None):
        if message is None:
            if min == -1:
                message = f"Ce champ doit contenir au plus {max} caractères"
            elif max == -1:
                message = f"Ce champ doit contenir au moins {min} caractères"
            else:
                message = (
                    f"Ce champ doit contenir entre {min} et {max} caractères"
                )
        super().__init__(min, max, message)


class NotReservedNameValidator:
    RESERVED_USERNAMES = ["admin", "root", "administrator", "system"]

    def __init__(self, message="Reserved username"):
        self.message = message

    def __call__(self, form, field):
        if field.data in self.RESERVED_USERNAMES:
            raise ValidationError(self.message)


class AlnumPlusValidator:
    def __init__(
        self,
        message=(
            "Username must be alphanumeric and the only special characters"
            " allowed are - and _"
        ),
    ):
        self.message = message

    def __call__(self, form, field):
        name = field.data
        name = name.replace("-", "")
        name = name.replace("_", "")
        if not name.isalnum():
            raise ValidationError(self.message)


class LoginTakenValidator:
    def __init__(self, message="Login already taken"):
        self.message = message

    def __call__(self, form, field):
        with db.session() as session:
            result = session.query(User).filter(User.id == field.data).first()
        if result is not None:
            raise ValidationError(self.message)
