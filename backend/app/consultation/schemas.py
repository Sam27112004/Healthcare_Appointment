import uuid
from typing import Any
from datetime import date
from pydantic import BaseModel, Field
from app.appointment.schemas import AppointmentResponse

class DoctorDashboardResponse(BaseModel):
    today_appointments: list[AppointmentResponse]
    upcoming_count: int
    completed_today: int
    pending_today: int

    class Config:
        from_attributes = True

class PreVisitSummaryResponse(BaseModel):
    appointment_id: uuid.UUID
    status: str
    summary: dict[str, Any]

    class Config:
        from_attributes = True

class ConsultationCreate(BaseModel):
    diagnosis: str | None = Field(None, max_length=500)
    notes: str = Field(..., max_length=5000)
    follow_up_date: date | None = None

class ConsultationResponse(BaseModel):
    id: uuid.UUID
    appointment_id: uuid.UUID
    diagnosis: str | None = None
    notes: str
    follow_up_date: date | None = None

    class Config:
        from_attributes = True

class MedicationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    dosage: str = Field(..., max_length=100)
    frequency: str = Field(..., max_length=100)
    duration: str = Field(..., max_length=100)
    instructions: str | None = Field(None, max_length=1000)
    start_date: date
    end_date: date

class PrescriptionCreate(BaseModel):
    notes: str | None = Field(None, max_length=1000)
    medications: list[MedicationCreate] = Field(..., min_length=1)

class MedicationResponse(BaseModel):
    id: uuid.UUID
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str | None = None
    start_date: date
    end_date: date

    class Config:
        from_attributes = True

class PrescriptionResponse(BaseModel):
    id: uuid.UUID
    consultation_id: uuid.UUID
    notes: str | None = None
    medications: list[MedicationResponse]

    class Config:
        from_attributes = True

class ConsultationCompleteResponse(BaseModel):
    id: uuid.UUID
    status: str
    ai_post_visit_status: str

    class Config:
        from_attributes = True
