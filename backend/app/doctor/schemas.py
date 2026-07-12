import uuid
from decimal import Decimal
from pydantic import BaseModel
from app.patient.schemas import UserSummary # Reusing the basic user summary

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
