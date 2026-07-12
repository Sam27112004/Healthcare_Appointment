import uuid
from sqlalchemy import String, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base

class Appointment(Base):
    __tablename__ = "appointment"

    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patient.id"), nullable=False, index=True)
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctor.id"), nullable=False, index=True)
    slot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("appointment_slot.id"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(20), default="booked", nullable=False, index=True)
    
    symptoms: Mapped[str | None] = mapped_column(Text)
    symptom_severity: Mapped[str | None] = mapped_column(String(10))
    
    ai_pre_visit_summary: Mapped[dict | None] = mapped_column(JSONB)
    ai_pre_visit_status: Mapped[str] = mapped_column(String(20), default="pending")
    
    ai_post_visit_summary: Mapped[dict | None] = mapped_column(JSONB)
    ai_post_visit_status: Mapped[str] = mapped_column(String(20), default="pending")
    
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    cancelled_by: Mapped[str | None] = mapped_column(String(20))
    booking_notes: Mapped[str | None] = mapped_column(Text)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments") # type: ignore
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments") # type: ignore
    slot: Mapped["AppointmentSlot"] = relationship("AppointmentSlot") # type: ignore
    consultation: Mapped["Consultation"] = relationship("Consultation", back_populates="appointment", uselist=False, cascade="all, delete-orphan") # type: ignore
    calendar_event: Mapped["CalendarEvent"] = relationship("CalendarEvent", back_populates="appointment", uselist=False, cascade="all, delete-orphan") # type: ignore

    __table_args__ = (
        Index("idx_appointment_doctor_date", "doctor_id", "created_at"),
    )
