import flask
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Length

from app.services import user


class Form(FlaskForm):
    class Meta:
        locales = ["fr", "fr_FR"]

    def validate(self, *args, **kwargs) -> bool:
        result = super().validate(*args, **kwargs)
        if not result:
            flask.flash(
                "Certains champs du formulaire comportent des erreurs", "error"
            )
        return result


class LoginField(StringField):
    def __init__(self, **kwargs):
        super().__init__(
            validators=[
                AlnumPlusValidator(),
                DataRequired(),
                Length(max=30),
                LoginTakenValidator(),
                NotReservedNameValidator(),
            ],
            **kwargs,
        )


class PasswordField(PasswordField):
    def __init__(self, **kwargs):
        validators = kwargs.pop("validators", [])
        validators.append(Length(min=4))
        super().__init__(
            validators=validators,
            **kwargs,
        )


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

    def __init__(self, message="Nom réservé"):
        self.message = message

    def __call__(self, form, field):
        if field.data in self.RESERVED_USERNAMES:
            raise ValidationError(self.message)


class AlnumPlusValidator:
    def __init__(
        self,
        message=(
            "Ce champ n'accepte que les caractères alphanumériques (A-Z 0-9),"
            " ainsi que les tirets (- et _)."
        ),
    ):
        self.message = message

    def __call__(self, form, field):
        name = field.data
        if not name:
            return
        name = name.replace("-", "")
        name = name.replace("_", "")
        if not name.isalnum():
            raise ValidationError(self.message)


class LoginTakenValidator:
    def __init__(self, message="Identifiant déjà pris"):
        self.message = message

    def __call__(self, form, field):
        if result := user.get_by_login(field.data):
            if current_user.is_authenticated and current_user.id == result.id:
                return
            raise ValidationError(self.message)
