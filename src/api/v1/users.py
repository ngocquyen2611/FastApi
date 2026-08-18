from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.passwords import verify_password
from src.core.security import create_access_token, get_current_user
from src.models.schemas.user import LogoutRequest, Token, UserLogin, UserOut, UserRegister, RefreshRequest
from src.models.schemas.email_verification import (
    RegisterResponse,
    REGISTER_SUCCESS_MESSAGE,
    ResendVerificationRequest,
    ResendVerificationResponse,
    RESEND_SUCCESS_MESSAGE,
    VerifyEmailRequest,
)
from src.models.user import User, UserStatus
from src.services import user_service, token_service
from src.models.schemas.password_reset import ResetPasswordRequest, ForgotPasswordRequest
from src.services.password_service import request_password_reset, reset_password as do_reset_password
from src.services import email_verification_service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=202)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, data.email)
    if existing_user:
        return RegisterResponse(detail=REGISTER_SUCCESS_MESSAGE)

    try:
        new_user = user_service.create_user(db, data)
    except ValueError:
        return RegisterResponse(detail=REGISTER_SUCCESS_MESSAGE)

    email_verification_service.send_verification_otp(db, new_user.user_id, new_user.email)
    return RegisterResponse(detail=REGISTER_SUCCESS_MESSAGE)


@router.post("/verify_email", response_model=UserOut)
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    return email_verification_service.verify_email(db, data.email, data.otp)


@router.post("/resend_verification", response_model=ResendVerificationResponse)
def resend_verification(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    email_verification_service.resend_verification_otp(db, data.email)
    return ResendVerificationResponse(detail=RESEND_SUCCESS_MESSAGE)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, data.email)

    if user is None:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    if not verify_password(data.password, user.user_detail.password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa được xác minh hoặc không thể đăng nhập",
        )

    access_token = create_access_token({"sub": str(user.user_id)})
    refresh_token = token_service.create_refresh_token(db, user.user_id)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    new_refresh_token, user_id = token_service.rotate_refresh_token(db, data.refresh_token)
    new_access_token = create_access_token({"sub": str(user_id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    token_service.revoke_refresh_token(db, data.refresh_token)
    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot_password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    request_password_reset(db, data.email)
    return {"detail": "Nếu email tồn tại, chúng tôi đã gửi hướng dẫn đặt lại mật khẩu"}


@router.post("/reset_password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    do_reset_password(db, data.token, data.new_password)
    return {"detail": "Đặt lại mật khẩu thành công"}
