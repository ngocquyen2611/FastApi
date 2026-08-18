from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.password_reset import PasswordResetToken
from src.core.security import (
    generate_reset_token_pair,
    hash_refresh_token,
    parse_raw_refresh_token,
    hash_password,
)
from src.services import user_service, token_service

RESET_TOKEN_EXPIRE_MINUTES = 15


def create_reset_token(db: Session, user_id: int) -> str:
    token_id, raw_token, token_hash = generate_reset_token_pair()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    record = PasswordResetToken(
        token_id=token_id,
        user_id=user_id,
        token_hash=token_hash,
        purpose="password_reset",
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    return raw_token


def request_password_reset(db: Session, email: str) -> None:

    user = user_service.get_user_by_email(db, email)
    if user is None:
        return 
    raw_token = create_reset_token(db, user.user_id)

    print(f"[DEV ONLY] Password reset token for {email}: {raw_token}")


def reset_password(db: Session, raw_token: str, new_password: str) -> None:
    try:
        token_id, raw_secret = parse_raw_refresh_token(raw_token)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    record = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_id == token_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if record.used_at is not None:
        raise HTTPException(status_code=400, detail="Reset token already used")

    if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if hash_refresh_token(raw_secret) != record.token_hash:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = user_service.get_user_by_id(db, record.user_id)
    user.user_detail.password = hash_password(new_password)
    record.used_at = datetime.now(timezone.utc)
    token_service.revoke_all_tokens_for_user(db, user.user_id)

    db.commit()