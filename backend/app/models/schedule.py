import uuid
from datetime import time, date
from sqlalchemy import Integer, Time, Boolean, ForeignKey, Date, String, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedule"

    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules") # type: ignore

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="chk_schedule_day"),
        CheckConstraint("start_time < end_time", name="chk_schedule_time"),
        UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_day"),
    )

class DoctorLeave(Base):
    __tablename__ = "doctor_leave"

    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False)
    leave_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))

    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="leaves") # type: ignore

    __table_args__ = (
        UniqueConstraint("doctor_id", "leave_date", name="uq_doctor_leave"),
        Index("idx_leave_doctor_date", "doctor_id", "leave_date"),
    )
