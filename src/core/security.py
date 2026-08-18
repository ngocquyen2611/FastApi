import jwt
from datetime import datetime, timedelta, timezone
import secrets
import hashlib

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.core.passwords import verify_password
import src.services

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
AccessTokenExpireMinutes = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=AccessTokenExpireMinutes)
    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except PyJWTError:
        raise credentials_exception

    user = src.services.user_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


def generate_refresh_token_pair() -> tuple[str, str, str]:
    token_id = secrets.token_urlsafe(16)   #ID public
    raw_secret = secrets.token_urlsafe(32)      # secret private
    raw_token = f"{token_id}.{raw_secret}"
    token_hash = hash_refresh_token(raw_secret)     # hash the secret for storage in the database
    return token_id, raw_token, token_hash

def hash_refresh_token(raw_secret: str) -> str:
    return hashlib.sha256(raw_secret.encode()).hexdigest()

def parse_raw_refresh_token(raw_token: str) -> tuple[str, str]:
    try: 
        token_id, raw_secret = raw_token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    return token_id, raw_secret
