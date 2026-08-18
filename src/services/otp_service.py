from datetime import datetime, timedelta, timezone
import secrets

from fastapi import HTTPException
from sqlalchemy import func
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
    # Vô hiệu hóa tất cả OTP cũ chưa được sử dụng
    old_otps = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user_id,
            OTPVerification.purpose == purpose,
            OTPVerification.used_at.is_(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for otp in old_otps:
        otp.used_at = now

    # Tạo OTP mới
    raw_otp = generate_otp()

    otp_record = OTPVerification(
        user_id=user_id,
        otp_hash=hash_password(raw_otp),
        purpose=purpose,
        expires_at=(
            now
            + timedelta(
                minutes=settings.email_otp_expire_minutes
            )
        ),
        attempt_count=0,
    )

    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

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
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

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

    if not verify_password(
        raw_otp,
        otp_record.otp_hash,
    ):
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


def resend_otp(
    db: Session,
    user_id: int,
    email: str,
    purpose: OTPPurpose,
) -> None:
    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 1. Lấy OTP gần nhất
    # ---------------------------------------------------------
    latest_otp = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user_id,
            OTPVerification.purpose == purpose,
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    # ---------------------------------------------------------
    # 2. Kiểm tra cooldown
    # ---------------------------------------------------------
    if latest_otp is not None:
        created_at = latest_otp.created_at

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        elapsed_seconds = (
            now - created_at
        ).total_seconds()

        if (
            elapsed_seconds
            < settings.email_otp_resend_cooldown_seconds
        ):
            remaining_seconds = max(
                1,
                int(
                    settings.email_otp_resend_cooldown_seconds
                    - elapsed_seconds
                ),
            )

            raise HTTPException(
                status_code=429,
                detail=(
                    f"Vui lòng thử lại sau "
                    f"{remaining_seconds} giây"
                ),
            )

    # ---------------------------------------------------------
    # 3. Kiểm tra giới hạn gửi OTP trong ngày
    # ---------------------------------------------------------
    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    tomorrow_start = today_start + timedelta(days=1)

    daily_send_count = (
        db.query(func.count(OTPVerification.otp_id))
        .filter(
            OTPVerification.user_id == user_id,
            OTPVerification.purpose == purpose,
            OTPVerification.created_at >= today_start,
            OTPVerification.created_at < tomorrow_start,
        )
        .scalar()
    )

    if (
        daily_send_count
        >= settings.email_otp_daily_send_limit
    ):
        raise HTTPException(
            status_code=429,
            detail=(
                "Bạn đã vượt quá số lần "
                "gửi OTP trong ngày"
            ),
        )

    # ---------------------------------------------------------
    # 4. Tạo OTP mới + gửi email
    # ---------------------------------------------------------
    create_and_send_otp(
        db=db,
        user_id=user_id,
        email=email,
        purpose=purpose,
    )