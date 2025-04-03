from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword",
                "password_confirm": "strongpassword",
                "first_name": "Иван",
                "last_name": "Иванов"
            }
        }

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    password_confirm: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Иван",
                "last_name": "Петров",
                "password": "newstrongpassword",
                "password_confirm": "newstrongpassword"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword"
            }
        }

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserList(BaseModel):
    users: List[UserResponse]
    total: int 