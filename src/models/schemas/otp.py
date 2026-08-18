from pydantic import BaseModel, EmailStr, field_validator


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower().strip()

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        value = value.strip()

        if not value.isdigit() or len(value) != 6:
            raise ValueError(
                "OTP phải gồm 6 chữ số"
            )

        return value


class ResendVerificationRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower().strip()