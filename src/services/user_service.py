# services/user_service.py
from sqlalchemy.orm import Session
from src.models.user import User, UserDetail
from src.models.schemas.user import UserRegister
from src.core.security import hash_password

from sqlalchemy.orm import joinedload

def get_user_by_email(db: Session, email: str):
    return (
        db.query(User)
        .options(joinedload(User.user_detail))
        .filter(User.email == email)
        .first()
    )

def create_user(db: Session, data: UserRegister):
    existing = get_user_by_email(db, data.email)
    if existing:
        raise ValueError("Email đã được sử dụng")

    hashed_password = hash_password(data.password)
    user = User(name=data.name, email=data.email)
    user_detail = UserDetail(password=hashed_password, user=user)
    db.add(user)
    db.add(user_detail)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()