from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, EmailStr
from src.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False) 
    # dữ liệu email phải là String vì nó đang theo SQLAlchemy
    full_name = Column(String, nullable=True)


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None

    class Config:
        from_attributes = True