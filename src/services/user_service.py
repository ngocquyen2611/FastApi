# services/user_service.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from src.core.passwords import hash_password
from src.models.schemas.user import UserRegister
from src.models.user import User, UserDetail, UserStatus


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
    user = User(name=data.name, email=data.email, status=UserStatus.PENDING_VERIFICATION)
    user_detail = UserDetail(password=hashed_password, user=user)
    db.add(user)
    db.add(user_detail)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Email đã được sử dụng")

    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()