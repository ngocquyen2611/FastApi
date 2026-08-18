from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.otp import OTPPurpose
from src.models.user import UserStatus
from src.services import otp_service, user_service


def verify_email(
    db: Session,
    email: str,
    otp: str,
):
    user = user_service.get_user_by_email(db, email)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="OTP không hợp lệ",
        )

    if user.status == UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Email đã được xác minh",
        )

    if user.status != UserStatus.PENDING_VERIFICATION:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản không thể xác minh",
        )

    otp_service.verify_otp(
        db=db,
        user_id=user.user_id,
        raw_otp=otp,
        purpose=OTPPurpose.EMAIL_VERIFICATION,
    )

    user.status = UserStatus.ACTIVE

    db.commit()
    db.refresh(user)

    return user