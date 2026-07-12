import uuid
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal
from datetime import time, date

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

class ScheduleCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    slot_duration: int = Field(..., ge=5, le=120, description="Duration in minutes")

class ScheduleUpdate(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    slot_duration: int | None = Field(None, ge=5, le=120)

class ScheduleResponse(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: int

    class Config:
        from_attributes = True

class LeaveCreate(BaseModel):
    leave_date: date
    reason: str | None = None

class LeaveResponse(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    leave_date: date
    reason: str | None = None

    class Config:
        from_attributes = True

class SlotGenerateRequest(BaseModel):
    start_date: date
    end_date: date

class SlotGenerateResponse(BaseModel):
    slots_created: int
    message: str
