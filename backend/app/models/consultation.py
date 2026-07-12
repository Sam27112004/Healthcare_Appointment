import uuid
from datetime import date
from sqlalchemy import Text, Date, ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Consultation(Base):
    __tablename__ = "consultation"

    appointment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("appointment.id", ondelete="CASCADE"), unique=True, nullable=False)
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctor.id"), nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_date: Mapped[date | None] = mapped_column(Date)

    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="consultation") # type: ignore
    prescription: Mapped["Prescription"] = relationship("Prescription", back_populates="consultation", uselist=False, cascade="all, delete-orphan")

class Prescription(Base):
    __tablename__ = "prescription"

    consultation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("consultation.id", ondelete="CASCADE"), unique=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    consultation: Mapped["Consultation"] = relationship("Consultation", back_populates="prescription")
    medications: Mapped[list["Medication"]] = relationship("Medication", back_populates="prescription", cascade="all, delete-orphan")

class Medication(Base):
    __tablename__ = "medication"

    prescription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prescription.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    prescription: Mapped["Prescription"] = relationship("Prescription", back_populates="medications")

    __table_args__ = (
        Index("idx_medication_dates", "start_date", "end_date"),
    )
