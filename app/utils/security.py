from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import delete, select
from app.database.Base import MyDb
from app.model import Admin, RefreshTokens
from app.utils.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def decode_token(token: str, expected_type: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"],
                             issuer="aljabr-api", audience="aljabr",
                             options={"require_exp": True, "require_sub": True, "require_iat": True})
        if payload.get("type") != expected_type or not isinstance(payload.get("version"), int):
            raise ValueError()
        int(payload["sub"])
        if not isinstance(payload.get("jti"), str):
            raise ValueError()
        return payload
    except (JWTError, ValueError, TypeError):
        raise HTTPException(401, "Token is invalid or expired", headers={"WWW-Authenticate": "Bearer"}) from None


def issue_tokens(db, user):
    now = datetime.now(timezone.utc)
    result = {"token_type": "bearer"}
    for kind, duration in (("access", timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)),
                           ("refresh", timedelta(days=settings.REFRESH_TOKEN_DAYS))):
        jti = str(uuid4())
        expiry = now + duration
        payload = {"sub": str(user.id), "version": user.token_version, "type": kind,
                   "iat": now, "exp": expiry, "jti": jti, "iss": "aljabr-api", "aud": "aljabr"}
        result[f"{kind}_token"] = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        if kind == "refresh":
            db.add(RefreshTokens(jti=jti, admin_id=user.id, expires_at=expiry.replace(tzinfo=None)))
    db.execute(delete(RefreshTokens).where(RefreshTokens.expires_at < now.replace(tzinfo=None)))
    return result


def get_current_admin(db: MyDb, token: str = Depends(bearer)):
    payload = decode_token(token, "access")
    user = db.scalar(select(Admin).where(Admin.id == int(payload["sub"])))
    if not user or not user.is_active or user.token_version != payload["version"]:
        raise HTTPException(401, "User is inactive or session has ended")
    return user


def revoke_sessions(db, user):
    user.token_version += 1
    db.execute(delete(RefreshTokens).where(RefreshTokens.admin_id == user.id))
