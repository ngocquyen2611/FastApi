from pydantic import BaseModel, EmailStr, field_validator
from src.models.user import UserStatus

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str 
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return v.lower().strip()

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    status: UserStatus

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return v.lower().strip()

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"