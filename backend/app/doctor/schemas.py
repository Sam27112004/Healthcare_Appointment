import uuid
from decimal import Decimal
from pydantic import BaseModel
from app.patient.schemas import UserSummary
from datetime import date, time

class SpecializationResponse(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True

class DoctorProfile(BaseModel):
    id: uuid.UUID
    user: UserSummary
    specialization: SpecializationResponse
    qualification: str | None = None
    experience_years: int | None = None
    bio: str | None = None
    consultation_fee: Decimal | None = None

    class Config:
        from_attributes = True

class SlotResponse(BaseModel):
    id: uuid.UUID
    start_time: time
    end_time: time
    status: str

    class Config:
        from_attributes = True

class DoctorSlotsResponse(BaseModel):
    doctor_id: uuid.UUID
    date: date
    slots: list[SlotResponse]
