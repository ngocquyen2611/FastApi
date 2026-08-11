from argon2 import verify_password
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.schemas.user import UserLogin, UserRegister, UserOut, Token
from src.services import user_service
from src.core.security import create_access_token, verify_password, get_current_user
from src.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email đã tồn tại")

    new_user = user_service.create_user(db, data)
    return new_user

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, data.email)

    if user is None:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    if not verify_password(data.password, user.user_detail.password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user