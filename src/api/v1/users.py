from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from src.models.schemas.user import LogoutRequest, Token, UserLogin, UserOut, UserRegister, RefreshRequest
from src.models.user import User, UserStatus
from src.services import user_service, token_service
from src.models.otp import OTPPurpose
from src.services import otp_service

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = user_service.get_user_by_email(db, data.email)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email đã tồn tại",
        )

    try:
        new_user = user_service.create_user(db, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail="Email đã tồn tại",
        ) from exc

    otp_service.create_and_send_otp(
        db=db,
        user_id=new_user.user_id,
        email=new_user.email,
        purpose=OTPPurpose.EMAIL_VERIFICATION,
    )

    return new_user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, data.email)

    if user is None:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    if not verify_password(data.password, user.user_detail.password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    access_token = create_access_token({"sub": user.email})
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