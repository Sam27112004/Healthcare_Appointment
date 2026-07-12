import uuid
from datetime import date
from sqlalchemy import String, Boolean, Date, Text, ForeignKey, Numeric, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True) # CHECK constraint handled in DB/Alembic or by app layer enum
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    patient_profile: Mapped["Patient"] = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    doctor_profile: Mapped["Doctor"] = relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Patient(Base):
    __tablename__ = "patient"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    blood_group: Mapped[str | None] = mapped_column(String(5))
    address: Mapped[str | None] = mapped_column(Text)
    medical_history: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship("User", back_populates="patient_profile")
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="patient") # type: ignore

class Doctor(Base):
    __tablename__ = "doctor"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("specialization.id"), nullable=False, index=True)
    qualification: Mapped[str | None] = mapped_column(String(255))
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    bio: Mapped[str | None] = mapped_column(Text)
    consultation_fee: Mapped[float | None] = mapped_column(Numeric(10, 2))

    user: Mapped["User"] = relationship("User", back_populates="doctor_profile")
    specialization: Mapped["Specialization"] = relationship("Specialization") # type: ignore
    schedules: Mapped[list["DoctorSchedule"]] = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan") # type: ignore
    leaves: Mapped[list["DoctorLeave"]] = relationship("DoctorLeave", back_populates="doctor", cascade="all, delete-orphan") # type: ignore
    slots: Mapped[list["AppointmentSlot"]] = relationship("AppointmentSlot", back_populates="doctor", cascade="all, delete-orphan") # type: ignore
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="doctor") # type: ignore
