from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    token_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    token_hash = Column(String, nullable=False)
    purpose = Column(String, nullable=False, default="password_reset")
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)          # NULL = chưa dùng
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")