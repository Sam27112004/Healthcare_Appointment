import uuid
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_event"

    appointment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("appointment.id", ondelete="CASCADE"), unique=True, nullable=False)
    patient_event_id: Mapped[str | None] = mapped_column(String(255))
    doctor_event_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)

    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="calendar_event") # type: ignore
