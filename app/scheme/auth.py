from pydantic import Field
from app.scheme.common import Schema


class Auth(Schema):
    refresh_token: str = Field(min_length=20, max_length=2048)


class TokenResponse(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PasswordChange(Schema):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


class AdminResponse(Schema):
    id: int
    username: str
    is_active: bool
