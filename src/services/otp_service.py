import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.passwords import hash_password, verify_password
from src.models.otp import OTPPurpose, OTPVerification
from src.services.email_service import send_otp_email


def generate_otp() -> str:
    return "".join(
        str(secrets.randbelow(10))
        for _ in range(settings.email_otp_length)
    )


def create_otp(
    db: Session,
    user_id: int,
    purpose: OTPPurpose,
) -> str:
    # Vô hiệu hóa các OTP cũ cùng purpose
    old_otps = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user_id,
            OTPVerification.purpose == purpose,
            OTPVerification.used_at.is_(None),
        )
        .all()
    )

    for otp in old_otps:
        otp.used_at = datetime.now(timezone.utc)

    # Tạo OTP mới
    raw_otp = generate_otp()

    otp_record = OTPVerification(
        user_id=user_id,
        otp_hash=hash_password(raw_otp),
        purpose=purpose,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=settings.email_otp_expire_minutes)
        ),
        attempt_count=0,
    )

    db.add(otp_record)
    db.commit()

    return raw_otp


def verify_otp(
    db: Session,
    user_id: int,
    raw_otp: str,
    purpose: OTPPurpose,
) -> None:
    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user_id,
            OTPVerification.purpose == purpose,
            OTPVerification.used_at.is_(None),
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if otp_record is None:
        raise HTTPException(
            status_code=400,
            detail="OTP không hợp lệ",
        )

    now = datetime.now(timezone.utc)

    expires_at = otp_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise HTTPException(
            status_code=400,
            detail="OTP đã hết hạn",
        )

    if otp_record.attempt_count >= settings.email_otp_max_attempts:
        raise HTTPException(
            status_code=400,
            detail="Bạn đã nhập sai OTP quá số lần cho phép",
        )

    if not verify_password(raw_otp, otp_record.otp_hash):
        otp_record.attempt_count += 1
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="OTP không chính xác",
        )

    otp_record.used_at = now
    db.commit()

def create_and_send_otp(
    db: Session,
    user_id: int,
    email: str,
    purpose: OTPPurpose,
) -> None:
    otp = create_otp(
        db=db,
        user_id=user_id,
        purpose=purpose,
    )

    send_otp_email(
        to_email=email,
        otp=otp,
        purpose=purpose.value,
    )