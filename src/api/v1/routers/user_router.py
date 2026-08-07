# routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.schemas.user import UserRegister, UserOut
from src.services import user_service

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):

    existing_user = user_service.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email đã tồn tại")

    new_user = user_service.create_user(db, data)

    return new_user