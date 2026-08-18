import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from src.models.base import Base


class OTPPurpose(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class OTPVerification(Base):
    __tablename__ = "otp_verification"

    otp_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("user.user_id"),
        nullable=False,
        index=True,
    )

    otp_hash = Column(String, nullable=False)

    purpose = Column(
        Enum(OTPPurpose),
        nullable=False,
    )

    expires_at = Column(DateTime, nullable=False)

    attempt_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    used_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    user = relationship("User")