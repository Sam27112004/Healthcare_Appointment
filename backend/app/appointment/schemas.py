import uuid
from pydantic import BaseModel, Field
from datetime import datetime, date, time

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

class AppointmentResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    slot: AppointmentSlotDetails
    status: str
    symptoms: str
    symptom_severity: str | None = None
    ai_pre_visit_status: str | None = None
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
