from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.enum_file import UserRole

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, description="Введите свое имя")
    email: EmailStr = Field(description="введите email, который будет логином")
    password: str = Field(min_length=6, max_length= 20, description="введите пароль от 6 до 20 символов")
    role: UserRole

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
