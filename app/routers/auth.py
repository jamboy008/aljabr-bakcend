from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, delete
from app.database.Base import MyDb
from app.model import Admin, RefreshTokens
from app.scheme.auth import Auth, TokenResponse, PasswordChange, AdminResponse
from app.utils.rate_limiting import limiter
from app.utils.security import (verify_password, hash_password, issue_tokens, decode_token,
                                get_current_admin, revoke_sessions)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, response: Response, db: MyDb, data: OAuth2PasswordRequestForm = Depends()):
    response.headers["Cache-Control"] = "no-store"
    user = db.scalar(select(Admin).where(Admin.username == data.username).with_for_update())
    if len(data.password) > 128:
        raise HTTPException(401, "Incorrect username or password")
    if user is None:
        # Spend the same expensive password hashing work for an unknown account.
        hash_password(data.password)
        raise HTTPException(401, "Incorrect username or password")
    if not verify_password(data.password, user.password) or not user.is_active:
        raise HTTPException(401, "Incorrect username or password")
    tokens = issue_tokens(db, user)
    db.commit()
    return tokens


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
def refresh(request: Request, response: Response, data: Auth, db: MyDb):
    response.headers["Cache-Control"] = "no-store"
    payload = decode_token(data.refresh_token, "refresh")
    user = db.scalar(select(Admin).where(Admin.id == int(payload["sub"])).with_for_update())
    if not user or not user.is_active or user.token_version != payload["version"]:
        raise HTTPException(401, "Session has ended")
    # Consume once, atomically: a refresh token cannot be replayed.
    result = db.execute(delete(RefreshTokens).where(
        RefreshTokens.jti == payload["jti"], RefreshTokens.admin_id == user.id))
    if result.rowcount != 1:
        raise HTTPException(401, "Refresh token has already been used or revoked")
    tokens = issue_tokens(db, user)
    db.commit()
    return tokens


@router.get("/me", response_model=AdminResponse)
def me(user=Depends(get_current_admin)):
    return user


@router.post("/logout", status_code=204)
def logout(db: MyDb, user=Depends(get_current_admin)):
    db.refresh(user, with_for_update=True)
    revoke_sessions(db, user)
    db.commit()


@router.post("/change-password", status_code=204)
@limiter.limit("5/minute")
def change_password(request: Request, data: PasswordChange, db: MyDb, user=Depends(get_current_admin)):
    db.refresh(user, with_for_update=True)
    if not verify_password(data.old_password, user.password):
        raise HTTPException(400, "Current password is incorrect")
    user.password = hash_password(data.new_password)
    revoke_sessions(db, user)
    db.commit()
