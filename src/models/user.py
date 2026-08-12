import enum

from sqlalchemy import Column, Enum, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"


# 1. USER
class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    # Relationships
    user_detail = relationship("UserDetail", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    wishlist_items = relationship("WishlistItem", back_populates="user")
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False,)


# 2. USER_DETAIL (Quan hệ 1:1 với User)
class UserDetail(Base):
    __tablename__ = "user_detail"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    phone = Column(String, unique=True, nullable=True)
    gender = Column(String, nullable=True)
    address = Column(String, nullable=True)
    password = Column(String, nullable=False)

    user = relationship("User", back_populates="user_detail")
