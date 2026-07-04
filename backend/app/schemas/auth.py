from pydantic import BaseModel, EmailStr, Field

class AuthRegister(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="StrongP@ssw0rd")
    # face_embedding will be uploaded later via separate endpoint

class AuthLogin(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="StrongP@ssw0rd")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
