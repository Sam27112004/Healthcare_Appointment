import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.slot import AppointmentSlot
from app.models.appointment import Appointment
from app.appointment.schemas import SlotHoldResponse, AppointmentCreate, AppointmentResponse
from app.schemas.enums import SlotStatus, AppointmentStatus

class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def hold_slot(self, user_id: uuid.UUID, slot_id: uuid.UUID) -> SlotHoldResponse:
        # We start a transaction inherently by using the session, but we want 
        # to ensure we lock the slot row so no one else can hold/book it simultaneously.
        
        # 1. Fetch and lock the requested slot
        stmt = select(AppointmentSlot).where(AppointmentSlot.id == slot_id).with_for_update(skip_locked=True)
        result = await self.db.execute(stmt)
        slot = result.scalar_one_or_none()

        if not slot:
            # It's either not found or currently locked by another transaction modifying it
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is no longer available")

        now = datetime.now(timezone.utc).replace(tzinfo=None) # We use naive UTC for DB

        if slot.status == SlotStatus.BOOKED.value or slot.status == SlotStatus.BLOCKED.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is no longer available")

        if slot.status == SlotStatus.HELD.value:
            # If held by someone else and not expired
            if slot.held_by_id != user_id and slot.held_until and slot.held_until > now:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is currently held by another user")

        # 2. Enforce "One hold per patient" rule. Release any other held slots for this user.
        # This requires locking those rows too to safely transition them.
        other_holds_stmt = select(AppointmentSlot).where(
            AppointmentSlot.held_by_id == user_id,
            AppointmentSlot.id != slot_id,
            AppointmentSlot.status == SlotStatus.HELD.value
        ).with_for_update()
        
        other_holds = (await self.db.execute(other_holds_stmt)).scalars().all()
        for other_slot in other_holds:
            other_slot.status = SlotStatus.AVAILABLE.value
            other_slot.held_by_id = None
            other_slot.held_until = None

        # 3. Update the targeted slot
        hold_duration_seconds = 600 # 10 minutes
        held_until = now + timedelta(seconds=hold_duration_seconds)
        
        slot.status = SlotStatus.HELD.value
        slot.held_by_id = user_id
        slot.held_until = held_until

        await self.db.commit()
        await self.db.refresh(slot)

        return SlotHoldResponse(
            slot_id=slot.id,
            status=slot.status,
            held_until=slot.held_until,
            ttl_seconds=hold_duration_seconds
        )

    async def book_appointment(self, user_id: uuid.UUID, data: AppointmentCreate) -> Appointment:
        # 1. Lock the slot
        slot_stmt = select(AppointmentSlot).where(AppointmentSlot.id == data.slot_id).with_for_update()
        slot = (await self.db.execute(slot_stmt)).scalar_one_or_none()

        if not slot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # 2. Validate hold
        if slot.status != SlotStatus.HELD.value or slot.held_by_id != user_id or not slot.held_until or slot.held_until < now:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot hold expired or invalid. Please hold the slot first.")

        # 3. Patient overlap validation
        # Ensure patient doesn't already have an appointment at this time
        overlap_stmt = (
            select(Appointment)
            .join(AppointmentSlot, Appointment.slot_id == AppointmentSlot.id)
            .where(
                Appointment.patient_id == user_id,
                AppointmentSlot.slot_date == slot.slot_date,
                AppointmentSlot.start_time == slot.start_time,
                Appointment.status != AppointmentStatus.CANCELLED.value
            )
        )
        overlap = (await self.db.execute(overlap_stmt)).scalar_one_or_none()
        
        if overlap:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already have an appointment booked for this date and time.")

        # 4. Create appointment and finalize slot
        slot.status = SlotStatus.BOOKED.value
        slot.held_by_id = None
        slot.held_until = None

        new_appointment = Appointment(
            patient_id=user_id,
            doctor_id=slot.doctor_id,
            slot_id=slot.id,
            status=AppointmentStatus.BOOKED.value,
            symptoms=data.symptoms,
            symptom_severity=data.symptom_severity,
            booking_notes=data.booking_notes,
            ai_pre_visit_status="processing"
        )
        self.db.add(new_appointment)

        await self.db.commit()

        # Reload with relationships for response
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.slot))
            .where(Appointment.id == new_appointment.id)
        )
        created_appt = (await self.db.execute(stmt)).scalar_one()

        # TODO: Dispatch Celery tasks here
        # generate_pre_visit_summary.delay(created_appt.id)
        # send_booking_confirmation.delay(created_appt.id)

        return created_appt
