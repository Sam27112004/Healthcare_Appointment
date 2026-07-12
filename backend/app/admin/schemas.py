import uuid
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal

class SpecializationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None

class SpecializationUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None

# We can reuse the SpecializationResponse or define an Admin specific one
class SpecializationResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None

    class Config:
        from_attributes = True

class DoctorCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=150)
    phone: str | None = None
    specialization_id: uuid.UUID
    qualification: str | None = None
    experience_years: int | None = None
    bio: str | None = None
    consultation_fee: Decimal | None = None

class DoctorUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=150)
    phone: str | None = None
    specialization_id: uuid.UUID | None = None
    qualification: str | None = None
    experience_years: int | None = None
    bio: str | None = None
    consultation_fee: Decimal | None = None
    is_active: bool | None = None
