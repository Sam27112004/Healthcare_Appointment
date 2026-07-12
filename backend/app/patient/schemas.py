import uuid
from datetime import date
from pydantic import BaseModel, Field

class UserSummary(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone: str | None = None

    class Config:
        from_attributes = True

class PatientProfile(BaseModel):
    id: uuid.UUID
    user: UserSummary
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    address: str | None = None
    medical_history: str | None = None

    class Config:
        from_attributes = True

class PatientUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=150)
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    address: str | None = None
    medical_history: str | None = None
