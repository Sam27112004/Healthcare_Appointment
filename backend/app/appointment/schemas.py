from typing import Any
import uuid
from pydantic import BaseModel, Field
from datetime import datetime, date, time

class UserBasic(BaseModel):
    full_name: str
    
    class Config:
        from_attributes = True

class DoctorBasic(BaseModel):
    id: uuid.UUID
    user: UserBasic

    class Config:
        from_attributes = True

class PatientBasic(BaseModel):
    id: uuid.UUID
    user: UserBasic

    class Config:
        from_attributes = True

class SlotHoldRequest(BaseModel):
    slot_id: uuid.UUID

class SlotHoldResponse(BaseModel):
    slot_id: uuid.UUID
    status: str
    held_until: datetime
    ttl_seconds: int

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    slot_id: uuid.UUID
    symptoms: str = Field(..., min_length=5, max_length=1000)
    symptom_severity: str | None = Field(None, pattern="^(mild|moderate|severe)$")
    booking_notes: str | None = Field(None, max_length=500)

class AppointmentSlotDetails(BaseModel):
    id: uuid.UUID
    slot_date: date
    start_time: time
    end_time: time

    class Config:
        from_attributes = True

class MedicationBasic(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str | None = None
    start_date: date
    end_date: date

    class Config:
        from_attributes = True

class PrescriptionBasic(BaseModel):
    notes: str | None = None
    medications: list[MedicationBasic]

    class Config:
        from_attributes = True

class ConsultationBasic(BaseModel):
    diagnosis: str | None = None
    notes: str
    follow_up_date: date | None = None
    prescription: PrescriptionBasic | None = None

    class Config:
        from_attributes = True

class AppointmentResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    doctor: DoctorBasic | None = None
    patient: PatientBasic | None = None
    slot: AppointmentSlotDetails
    consultation: ConsultationBasic | None = None
    status: str
    symptoms: str
    symptom_severity: str | None = None
    ai_pre_visit_status: str | None = None
    ai_pre_visit_summary: dict | None = None
    ai_post_visit_status: str | None = None
    ai_post_visit_summary: dict | None = None
    created_at: datetime
    cancellation_reason: str | None = None
    cancelled_by: str | None = None

    class Config:
        from_attributes = True

class AppointmentCancelRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)

class AppointmentCancelResponse(BaseModel):
    id: uuid.UUID
    status: str
    cancellation_reason: str | None = None
    cancelled_by: str | None = None

class AppointmentRescheduleRequest(BaseModel):
    new_slot_id: uuid.UUID

class AppointmentRescheduleResponse(BaseModel):
    id: uuid.UUID
    status: str
    slot: AppointmentSlotDetails
    previous_slot: AppointmentSlotDetails
