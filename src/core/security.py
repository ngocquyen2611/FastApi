import jwt
from datetime import datetime, timedelta, timezone

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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = src.services.user_service.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user