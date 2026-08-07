from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str 

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}