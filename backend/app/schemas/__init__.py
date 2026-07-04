from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .auth import AuthRegister, AuthLogin, TokenResponse

class UserResponse(BaseModel):
    id: str
    email: str
    has_face_embedding: bool
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

class AnalyticsResponse(BaseModel):
    total_users: int
    users_with_faces: int
    system_status: str

__all__ = [
    "AuthRegister", "AuthLogin", "TokenResponse",
    "UserResponse", "UserUpdate", "AnalyticsResponse"
]
