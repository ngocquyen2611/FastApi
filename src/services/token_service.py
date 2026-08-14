from datetime import datetime, timedelta, timezone 

from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.token import RefreshToken
from src.core.security import (
    generate_refresh_token_pair,
    hash_refresh_token,
    parse_raw_refresh_token,
)
from src.core.config import settings

REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

def create_refresh_token(db: Session, user_id: int) -> str:
    token_id, raw_token, token_hash = generate_refresh_token_pair()
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    record = RefreshToken(
        token_id=token_id,
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(record)
    db.commit()
    return raw_token

def rotate_refresh_token(db: Session, raw_token: str) -> tuple[str, int]:
    """Verify token cũ, revoke nó, cấp token mới. Trả về (raw_token_mới, user_id)."""
    token_id, raw_secret = parse_raw_refresh_token(raw_token)

    record = db.query(RefreshToken).filter(RefreshToken.token_id == token_id).first()
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if record.revoked:
        revoke_all_tokens_for_user(db, record.user_id)
        raise HTTPException(status_code=401, detail="Refresh token reuse detected")

    if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    if hash_refresh_token(raw_secret) != record.token_hash:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_token_id, new_raw_token, new_token_hash = generate_refresh_token_pair()
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    record.revoked = True
    record.revoked_at = datetime.now(timezone.utc)
    record.replaced_by = new_token_id

    new_record = RefreshToken(
        token_id=new_token_id,
        user_id=record.user_id,
        token_hash=new_token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(new_record)
    db.commit()

    return new_raw_token, record.user_id


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    token_id, _ = parse_raw_refresh_token(raw_token)
    record = db.query(RefreshToken).filter(RefreshToken.token_id == token_id).first()
    if record and not record.revoked:
        record.revoked = True
        record.revoked_at = datetime.now(timezone.utc)
        db.commit()


def revoke_all_tokens_for_user(db: Session, user_id:int) ->None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({"revoked": True, "revoked_at": datetime.now(timezone.utc)})
    db.commit()