import urllib

import requests
from pydantic import BaseModel as Model
from requests import Session

from app import app, config
from app.db import User

BASE_URL = "https://discord.com"
API_URL = f"{BASE_URL}/api/v10"
CDN_URL = "https://cdn.discordapp.com"
SCOPES = ("email", "identify")

session = Session()
session.headers["Content-Type"] = "application/x-www-form-urlencoded"


class AuthorizationParams(Model):
    client_id: str = config.DISCORD_CLIENT_ID
    redirect_uri: str
    response_type: str = "code"
    scope: str = " ".join(SCOPES)
    state: str | None


def get_authorization_url(state: str = None):
    url = "https://discord.com/oauth2/authorize"
    redirect = app.url_for("discord_callback", _external=True)
    params = AuthorizationParams(state=state, redirect_uri=redirect)
    return f"{url}?" + urllib.parse.urlencode(
        params.model_dump(exclude_none=True)
    )


class AccessTokenRequest(Model):
    grant_type: str = "authorization_code"
    code: str
    redirect_uri: str


class AccessTokenResponse(Model):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


def get_discord_token(code: str) -> AccessTokenResponse:
    url = f"{API_URL}/oauth2/token"
    data = AccessTokenRequest(
        code=code, redirect_uri=app.url_for("discord_callback", _external=True)
    )
    response = session.post(
        url,
        data=data.model_dump(),
        auth=(config.DISCORD_CLIENT_ID, config.DISCORD_CLIENT_SECRET),
    )
    response.raise_for_status()
    return AccessTokenResponse(**response.json())


class RefreshTokenRequest(Model):
    grant_type: str = "refresh_token"
    refresh_token: str


def refresh(refresh_token: str) -> AccessTokenResponse:
    url = f"{API_URL}/oauth2/token"
    data = RefreshTokenRequest(refresh_token=refresh_token)
    response = session.post(
        url,
        data=data.model_dump(),
        auth=(config.DISCORD_CLIENT_ID, config.DISCORD_CLIENT_SECRET),
    )
    response.raise_for_status()
    return AccessTokenResponse(**response.json())


class API:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def request(self, method, url: str, **kwargs):
        api = kwargs.pop("api", True)
        base = API_URL if api else BASE_URL
        url = base + url
        response = requests.request(
            method,
            url,
            data=kwargs,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        response.raise_for_status()
        return response.json()

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)

    class User(Model):
        id: str
        username: str
        discriminator: str
        global_name: str | None
        avatar: str | None
        bot: bool | None = None
        system: bool | None = None
        mfa_enabled: bool | None
        banner: str | None
        accent_color: int | None
        locale: str | None
        verified: bool | None
        email: str | None
        flags: int | None
        premium_type: int | None
        public_flags: int | None
        avatar_decoration_data: dict | None

        def __str__(self):
            return self.name

        @property
        def name(self):
            return self.global_name or self.username

        @property
        def avatar_url(self):
            if not self.avatar:
                return None
            return (
                f"{CDN_URL}/avatars/{self.id}"
                f"/{self.avatar}.webp?size={config.DISCORD_AVATAR_SIZE}"
            )

    def get_user(self) -> "API.User":
        data = self.get("/users/@me")
        return self.User(**data)

    def get_oauth(self):
        return self.get("/oauth2/@me")


def get_db_user(access_token) -> User | None:
    api = API(access_token)
    user = api.get_user()
    with app.session() as s:
        user = (
            s.query(User).filter_by(discord_id=user.id)
            or s.query(User).filter_by(email=user.email)
        ).first()
    return user


def refresh_avatars(login=None):
    refreshed_users = []
    with app.session() as s:
        query = s.query(User).filter_by(image_type=User.ImageType.discord)
        if login:
            query = query.filter_by(login=login)
        for user in query:
            if not user.refresh_avatar():
                continue
            s.commit()
            refreshed_users.append(repr(user))
    return refreshed_users


def refresh_tokens(login=None):
    refreshed_users = []
    with app.session() as s:
        query = s.query(User).filter(User.discord_id is not None)
        if login:
            query = query.filter_by(login=login)
        for user in query:
            if not user.refresh_discord_token():
                continue
            s.commit()
            refreshed_users.append(repr(user))
    return refreshed_users
