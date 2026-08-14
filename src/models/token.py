from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.models.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    token_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by = Column(String, nullable=True)            
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")