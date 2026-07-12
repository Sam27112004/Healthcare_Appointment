import uuid
from datetime import date
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    role: str

class UserResponse(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class PatientRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=150)
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    address: str | None = None
    medical_history: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse | None = None # Included on login/register

class RefreshRequest(BaseModel):
    refresh_token: str
