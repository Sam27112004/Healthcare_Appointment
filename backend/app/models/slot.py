import uuid
from datetime import time, date, datetime
from sqlalchemy import Date, Time, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime
from app.models.base import Base

class AppointmentSlot(Base):
    __tablename__ = "appointment_slot"

    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False)
    slot_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False, index=True)
    held_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user.id"))
    held_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="slots") # type: ignore
    user: Mapped["User"] = relationship("User") # type: ignore

    __table_args__ = (
        UniqueConstraint("doctor_id", "slot_date", "start_time", name="uq_doctor_slot"),
        Index("idx_slot_doctor_date", "doctor_id", "slot_date"),
        Index("idx_slot_held_until", "held_until", postgresql_where=(status == 'held')),
    )
