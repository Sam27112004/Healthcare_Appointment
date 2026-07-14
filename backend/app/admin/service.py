import uuid
from datetime import date, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload, joinedload
from app.models.specialization import Specialization
from app.models.user import Doctor, User, Patient
from app.models.schedule import DoctorSchedule, DoctorLeave
from app.models.slot import AppointmentSlot
from app.models.appointment import Appointment
from app.admin.schemas import (
    SpecializationCreate, SpecializationUpdate, DoctorCreate, DoctorUpdate,
    ScheduleCreate, ScheduleUpdate, LeaveCreate
)
from app.auth.security import get_password_hash
from app.schemas.enums import Role, SlotStatus
from app.schemas.common import PaginatedResponse
from app.doctor.schemas import DoctorProfile
from app.notifications.tasks import send_leave_notification_task

class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ================= Specialization Management =================

    async def get_specializations(self) -> list[Specialization]:
        stmt = select(Specialization)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_specialization(self, spec_id: uuid.UUID) -> Specialization:
        stmt = select(Specialization).where(Specialization.id == spec_id)
        result = await self.db.execute(stmt)
        spec = result.scalar_one_or_none()
        if not spec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found")
        return spec

    async def create_specialization(self, data: SpecializationCreate) -> Specialization:
        # Check uniqueness of name
        stmt = select(Specialization).where(func.lower(Specialization.name) == data.name.lower())
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization with this name already exists")
            
        spec = Specialization(
            name=data.name,
            description=data.description
        )
        self.db.add(spec)
        await self.db.commit()
        await self.db.refresh(spec)
        return spec

    async def update_specialization(self, spec_id: uuid.UUID, data: SpecializationUpdate) -> Specialization:
        spec = await self.get_specialization(spec_id)
        
        if data.name is not None:
            # Check uniqueness of new name
            if data.name.lower() != spec.name.lower():
                stmt = select(Specialization).where(func.lower(Specialization.name) == data.name.lower())
                existing = (await self.db.execute(stmt)).scalar_one_or_none()
                if existing:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization with this name already exists")
            spec.name = data.name
            
        if data.description is not None:
            spec.description = data.description
            
        await self.db.commit()
        await self.db.refresh(spec)
        return spec

    async def delete_specialization(self, spec_id: uuid.UUID) -> None:
        spec = await self.get_specialization(spec_id)
        
        # Guard: check if any doctors are currently assigned to this specialization
        stmt = select(Doctor).where(Doctor.specialization_id == spec_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot delete specialization that is assigned to one or more doctors"
            )
            
        await self.db.delete(spec)
        await self.db.commit()

    # ================= Doctor Management =================

    async def get_doctors(self, page: int = 1, limit: int = 20) -> PaginatedResponse[DoctorProfile]:
        # This differs from the public search_doctors by returning ALL doctors (even inactive ones)
        # Admins need to see inactive ones to reactivate them if needed.
        stmt = select(Doctor).join(User).options(
            selectinload(Doctor.user),
            selectinload(Doctor.specialization)
        )
        count_stmt = select(func.count(Doctor.id)).join(User)

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        doctors = result.scalars().all()
        
        items = [DoctorProfile.model_validate(doc) for doc in doctors]
        return PaginatedResponse.create(items=items, total=total, page=page, limit=limit)

    async def create_doctor(self, data: DoctorCreate) -> Doctor:
        # Check if email exists
        stmt = select(User).where(User.email == data.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Verify specialization exists
        spec_stmt = select(Specialization).where(Specialization.id == data.specialization_id)
        spec = (await self.db.execute(spec_stmt)).scalar_one_or_none()
        if not spec:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization not found")

        # Create user
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role=Role.DOCTOR.value,
            is_active=True
        )
        self.db.add(user)
        await self.db.flush() # flush to get user.id

        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            specialization_id=data.specialization_id,
            qualification=data.qualification,
            experience_years=data.experience_years,
            bio=data.bio,
            consultation_fee=data.consultation_fee
        )
        self.db.add(doctor)
        
        await self.db.commit()
        # Fetch the complete doctor with relationships
        return await self._get_doctor_with_rels(doctor.id)

    async def _get_doctor_with_rels(self, doctor_id: uuid.UUID) -> Doctor:
        stmt = select(Doctor).where(Doctor.id == doctor_id).options(
            selectinload(Doctor.user),
            selectinload(Doctor.specialization)
        )
        result = await self.db.execute(stmt)
        doctor = result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        return doctor

    async def update_doctor(self, doctor_id: uuid.UUID, data: DoctorUpdate) -> Doctor:
        doctor = await self._get_doctor_with_rels(doctor_id)

        # Update User fields
        if data.full_name is not None:
            doctor.user.full_name = data.full_name
        if data.phone is not None:
            doctor.user.phone = data.phone
        if data.is_active is not None:
            doctor.user.is_active = data.is_active

        # Update Doctor fields
        if data.specialization_id is not None:
            spec_stmt = select(Specialization).where(Specialization.id == data.specialization_id)
            spec = (await self.db.execute(spec_stmt)).scalar_one_or_none()
            if not spec:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization not found")
            doctor.specialization_id = data.specialization_id

        if data.qualification is not None:
            doctor.qualification = data.qualification
        if data.experience_years is not None:
            doctor.experience_years = data.experience_years
        if data.bio is not None:
            doctor.bio = data.bio
        if data.consultation_fee is not None:
            doctor.consultation_fee = data.consultation_fee

        await self.db.commit()
        return await self._get_doctor_with_rels(doctor_id)

    async def deactivate_doctor(self, doctor_id: uuid.UUID) -> None:
        doctor = await self._get_doctor_with_rels(doctor_id)
        doctor.user.is_active = False
        await self.db.commit()

    # ================= Schedule & Leave Management =================

    async def create_schedule(self, doctor_id: uuid.UUID, data: ScheduleCreate) -> DoctorSchedule:
        # Check if doctor exists
        await self._get_doctor_with_rels(doctor_id)

        if data.start_time >= data.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must be before end time")

        # Check for overlapping schedules on the same day for this doctor
        stmt = select(DoctorSchedule).where(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.day_of_week == data.day_of_week
        )
        existing_schedules = (await self.db.execute(stmt)).scalars().all()
        for sched in existing_schedules:
            if not (data.end_time <= sched.start_time or data.start_time >= sched.end_time):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Schedule overlaps with an existing schedule for this day")

        schedule = DoctorSchedule(
            doctor_id=doctor_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            slot_duration=data.slot_duration
        )
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def update_schedule(self, doctor_id: uuid.UUID, schedule_id: uuid.UUID, data: ScheduleUpdate) -> DoctorSchedule:
        stmt = select(DoctorSchedule).where(DoctorSchedule.id == schedule_id, DoctorSchedule.doctor_id == doctor_id)
        schedule = (await self.db.execute(stmt)).scalar_one_or_none()
        
        if not schedule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

        # Create temporary variables to check overlaps and logic
        new_start = data.start_time if data.start_time is not None else schedule.start_time
        new_end = data.end_time if data.end_time is not None else schedule.end_time

        if new_start >= new_end:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must be before end time")

        if data.start_time or data.end_time:
            overlap_stmt = select(DoctorSchedule).where(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.day_of_week == schedule.day_of_week,
                DoctorSchedule.id != schedule_id
            )
            existing_schedules = (await self.db.execute(overlap_stmt)).scalars().all()
            for sched in existing_schedules:
                if not (new_end <= sched.start_time or new_start >= sched.end_time):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Updated schedule overlaps with another schedule")

        if data.start_time is not None:
            schedule.start_time = data.start_time
        if data.end_time is not None:
            schedule.end_time = data.end_time
        if data.slot_duration is not None:
            schedule.slot_duration = data.slot_duration

        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def create_leave(self, doctor_id: uuid.UUID, data: LeaveCreate) -> DoctorLeave:
        await self._get_doctor_with_rels(doctor_id)

        # Check if already on leave
        stmt = select(DoctorLeave).where(DoctorLeave.doctor_id == doctor_id, DoctorLeave.leave_date == data.leave_date)
        if (await self.db.execute(stmt)).scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Doctor is already on leave for this date")

        # Mark leave
        leave = DoctorLeave(
            doctor_id=doctor_id,
            leave_date=data.leave_date,
            reason=data.reason
        )
        self.db.add(leave)

        # Block affected slots
        slot_stmt = select(AppointmentSlot).where(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.slot_date == data.leave_date,
            AppointmentSlot.status == SlotStatus.AVAILABLE.value
        ).with_for_update() # Protect from concurrent booking while blocking
        
        slots = (await self.db.execute(slot_stmt)).scalars().all()
        for slot in slots:
            slot.status = SlotStatus.BLOCKED.value

        # TODO: Trigger Celery task to email patients with booked appointments on this day

        await self.db.commit()
        await self.db.refresh(leave)
        return leave

    async def delete_leave(self, doctor_id: uuid.UUID, leave_id: uuid.UUID) -> None:
        stmt = select(DoctorLeave).where(DoctorLeave.id == leave_id, DoctorLeave.doctor_id == doctor_id)
        leave = (await self.db.execute(stmt)).scalar_one_or_none()
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave not found")
            
        self.db.delete(leave)
        
        # Unblock slots
        slot_stmt = select(AppointmentSlot).where(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.slot_date == leave.leave_date,
            AppointmentSlot.status == SlotStatus.BLOCKED.value
        ).with_for_update()
        
        slots = (await self.db.execute(slot_stmt)).scalars().all()
        for slot in slots:
            slot.status = SlotStatus.AVAILABLE.value

        await self.db.commit()

    # ================= Slot Generation =================

    async def generate_slots(self, doctor_id: uuid.UUID, start_date: date, end_date: date) -> int:
        if start_date > end_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_date must be before end_date")
        
        # Limit generation to 60 days max to prevent overload
        if (end_date - start_date).days > 60:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot generate slots for more than 60 days at a time")

        await self._get_doctor_with_rels(doctor_id)

        # Get all schedules for doctor
        schedule_stmt = select(DoctorSchedule).where(DoctorSchedule.doctor_id == doctor_id)
        schedules = (await self.db.execute(schedule_stmt)).scalars().all()
        
        if not schedules:
            return 0 # No schedules, no slots to generate

        # Map schedules by day_of_week for O(1) lookup
        schedules_by_day = {i: [] for i in range(7)}
        for s in schedules:
            schedules_by_day[s.day_of_week].append(s)

        # Get all leaves for the doctor in this date range
        leave_stmt = select(DoctorLeave).where(
            DoctorLeave.doctor_id == doctor_id,
            DoctorLeave.leave_date >= start_date,
            DoctorLeave.leave_date <= end_date
        )
        leaves = (await self.db.execute(leave_stmt)).scalars().all()
        leave_dates = {l.leave_date for l in leaves}

        slots_created = 0
        current_date = start_date

        while current_date <= end_date:
            day_of_week = current_date.weekday() # 0 = Monday, 6 = Sunday
            daily_schedules = schedules_by_day[day_of_week]

            for sched in daily_schedules:
                # Iterate from start_time to end_time
                current_time = datetime.combine(current_date, sched.start_time)
                end_time = datetime.combine(current_date, sched.end_time)
                duration = timedelta(minutes=sched.slot_duration)

                while current_time + duration <= end_time:
                    slot_start = current_time.time()
                    slot_end = (current_time + duration).time()
                    
                    # Check if slot already exists
                    existing_stmt = select(AppointmentSlot).where(
                        AppointmentSlot.doctor_id == doctor_id,
                        AppointmentSlot.slot_date == current_date,
                        AppointmentSlot.start_time == slot_start
                    )
                    existing_slot = (await self.db.execute(existing_stmt)).scalar_one_or_none()
                    
                    if not existing_slot:
                        # Create the slot
                        status_val = SlotStatus.BLOCKED.value if current_date in leave_dates else SlotStatus.AVAILABLE.value
                        
                        new_slot = AppointmentSlot(
                            doctor_id=doctor_id,
                            slot_date=current_date,
                            start_time=slot_start,
                            end_time=slot_end,
                            status=status_val
                        )
                        self.db.add(new_slot)
                        slots_created += 1

                    current_time += duration

            current_date += timedelta(days=1)

        await self.db.commit()
        return slots_created

    async def get_stats(self) -> dict:
        # Count total doctors
        doctor_count = await self.db.scalar(select(func.count(Doctor.id)))
        
        # Count total patients
        patient_count = await self.db.scalar(select(func.count(Patient.id)))
        
        # Count appointments for today
        today = datetime.now().date()
        appointments_today = await self.db.scalar(
            select(func.count(Appointment.id))
            .join(AppointmentSlot, Appointment.slot_id == AppointmentSlot.id)
            .where(AppointmentSlot.slot_date == today)
        )
        
        return {
            "total_doctors": doctor_count or 0,
            "total_patients": patient_count or 0,
            "appointments_today": appointments_today or 0
        }
