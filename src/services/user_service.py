from sqlalchemy.orm import Session
from src.models.base import User

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self):
        return self.db.query(User).all()

    def create_user(self, email: str, full_name: str | None = None):
        user = User(email=email, full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id: int, email:str | None, full_name:str | None):
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        self.db.delete(user)
        self.db.commit()
        return user