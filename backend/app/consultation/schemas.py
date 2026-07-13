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
