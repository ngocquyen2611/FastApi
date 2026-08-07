# services/user_service.py
from sqlalchemy.orm import Session
from src.models.user import User, UserDetail
from src.models.schemas.user import UserRegister
from src.core.security import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, data: UserRegister):
    # TODO:
    # 1. hash_password(data.password)
    # 2. tạo object User(name=..., email=...)
    # 3. tạo object UserDetail(password=hash) liên kết với User vừa tạo
    # 4. db.add(...), db.commit(), db.refresh(...)
    # 5. return user vừa tạo
    hashed_password = hash_password(data.password)
    user = User(name=data.name, email=data.email)
    user_detail = UserDetail(password=hashed_password, user=user)
    db.add(user)
    db.add(user_detail)
    db.commit()
    db.refresh(user)
    return user