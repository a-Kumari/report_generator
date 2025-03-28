from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"  
    admin_key: str | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        form_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


from pydantic import BaseModel

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None


class ReportOut(BaseModel):
    report_id: int
    user_id: int
    status: str
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        form_attributes = True 


class UserCreateResponse(BaseModel):
    username: str
    email: str
    role: str  