import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.services import user_service


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        sub = payload.get("sub")

        if sub is None:
            raise credentials_exception

        user_id = int(sub)

    except (PyJWTError, ValueError, TypeError):
        raise credentials_exception

    user = user_service.get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise credentials_exception

    return user


def generate_refresh_token_pair() -> tuple[str, str, str]:
    token_id = secrets.token_urlsafe(16)

    raw_secret = secrets.token_urlsafe(32)

    raw_token = f"{token_id}.{raw_secret}"

    token_hash = hash_refresh_token(raw_secret)

    return token_id, raw_token, token_hash


def hash_refresh_token(raw_secret: str) -> str:
    return hashlib.sha256(
        raw_secret.encode()
    ).hexdigest()


def parse_raw_refresh_token(raw_token: str) -> tuple[str, str]:
    try:
        token_id, raw_secret = raw_token.split(".", 1)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid refresh token",
        )

    return token_id, raw_secret
