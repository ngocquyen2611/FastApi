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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"