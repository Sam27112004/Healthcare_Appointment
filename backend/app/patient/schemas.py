import uuid
from datetime import date, time, datetime
from pydantic import BaseModel, Field
from app.appointment.schemas import DoctorBasic

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

class DoctorSummary(BaseModel):
    id: uuid.UUID
    full_name: str
    specialization: str

    class Config:
        from_attributes = True

class SlotSummary(BaseModel):
    id: uuid.UUID
    slot_date: date
    start_time: time
    end_time: time

    class Config:
        from_attributes = True

class PatientAppointmentResponse(BaseModel):
    id: uuid.UUID
    doctor: DoctorBasic
    slot: SlotSummary
    status: str
    symptoms: str
    ai_pre_visit_status: str | None = None
    ai_post_visit_status: str | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True
    
class PaginatedPatientAppointments(BaseModel):
    items: list[PatientAppointmentResponse]
    total: int
    page: int
    limit: int
    pages: int
