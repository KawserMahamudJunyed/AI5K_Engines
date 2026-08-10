from pydantic import BaseModel, EmailStr
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
