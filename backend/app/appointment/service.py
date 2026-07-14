import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from app.models.slot import AppointmentSlot
from app.models.appointment import Appointment
from app.models.user import User, Patient, Doctor
from app.appointment.schemas import SlotHoldResponse, AppointmentCreate, AppointmentResponse, AppointmentCancelResponse, AppointmentRescheduleResponse
from app.schemas.enums import SlotStatus, AppointmentStatus, Role
from app.ai.tasks import generate_pre_visit_summary_task
from app.notifications.tasks import (
    send_booking_confirmation_task,
    send_cancellation_email_task,
    send_reschedule_email_task
)
from app.calendar.tasks import (
    create_calendar_event_task,
    update_calendar_event_task,
    delete_calendar_event_task
)

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

        now = datetime.now(timezone.utc) # We use naive UTC for DB

        if slot.status == SlotStatus.BOOKED.value or slot.status == SlotStatus.BLOCKED.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is no longer available")

        if slot.status == SlotStatus.HELD.value:
            # If held by someone else and not expired
            if slot.held_by != user_id and slot.held_until and slot.held_until > now:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is currently held by another user")

        # 2. Enforce "One hold per patient" rule. Release any other held slots for this user.
        # This requires locking those rows too to safely transition them.
        other_holds_stmt = select(AppointmentSlot).where(
            AppointmentSlot.held_by == user_id,
            AppointmentSlot.id != slot_id,
            AppointmentSlot.status == SlotStatus.HELD.value
        ).with_for_update()
        
        other_holds = (await self.db.execute(other_holds_stmt)).scalars().all()
        for other_slot in other_holds:
            other_slot.status = SlotStatus.AVAILABLE.value
            other_slot.held_by = None
            other_slot.held_until = None

        # 3. Update the targeted slot
        hold_duration_seconds = 600 # 10 minutes
        held_until = now + timedelta(seconds=hold_duration_seconds)
        
        slot.status = SlotStatus.HELD.value
        slot.held_by = user_id
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

        now = datetime.now(timezone.utc)

        # 2. Validate hold
        print(f"DEBUG book_appointment: slot.status={slot.status}, slot.held_by={slot.held_by}, user_id={user_id}, slot.held_until={slot.held_until}, now={now}")
        if slot.status != SlotStatus.HELD.value or slot.held_by != user_id or not slot.held_until or slot.held_until < now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot is not held by you or hold has expired")

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

        # 4. Book it
        
        patient_stmt = select(Patient).where(Patient.user_id == user_id)
        patient = (await self.db.execute(patient_stmt)).scalar_one_or_none()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

        slot.status = SlotStatus.BOOKED.value
        slot.held_by = None
        slot.held_until = None

        new_appointment = Appointment(
            patient_id=patient.id,
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

        # Dispatch Celery tasks
        generate_pre_visit_summary_task.delay(str(created_appt.id))
        send_booking_confirmation_task.delay(str(created_appt.id))
        create_calendar_event_task.delay(str(created_appt.id))

        return created_appt

    async def cancel_appointment(self, appointment_id: uuid.UUID, current_user: User, reason: str | None) -> AppointmentCancelResponse:
        # Lock appointment
        stmt = select(Appointment).options(selectinload(Appointment.slot)).where(Appointment.id == appointment_id).with_for_update()
        appointment = (await self.db.execute(stmt)).scalar_one_or_none()

        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

        if current_user.role == Role.PATIENT.value and appointment.patient_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this appointment")
            
        if current_user.role == Role.DOCTOR.value and appointment.doctor_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this appointment")

        if appointment.status == AppointmentStatus.CANCELLED.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appointment is already cancelled")

        if appointment.status == AppointmentStatus.COMPLETED.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel a completed appointment")

        # Update appointment
        appointment.status = AppointmentStatus.CANCELLED.value
        appointment.cancellation_reason = reason
        appointment.cancelled_by = current_user.role
        
        # Update slot (need to lock the slot specifically if it wasn't locked with appointment)
        slot_stmt = select(AppointmentSlot).where(AppointmentSlot.id == appointment.slot_id).with_for_update()
        slot = (await self.db.execute(slot_stmt)).scalar_one()
        slot.status = SlotStatus.AVAILABLE.value
        
        await self.db.commit()

        send_cancellation_email_task.delay(str(appointment.id))
        delete_calendar_event_task.delay(str(appointment.id))

        return AppointmentCancelResponse(
            id=appointment.id,
            status=appointment.status,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_by=appointment.cancelled_by
        )

    async def reschedule_appointment(self, appointment_id: uuid.UUID, current_user: User, new_slot_id: uuid.UUID) -> AppointmentRescheduleResponse:
        if current_user.role != Role.PATIENT.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can reschedule appointments")

        # 1. Lock appointment
        stmt = select(Appointment).options(selectinload(Appointment.slot)).where(Appointment.id == appointment_id).with_for_update()
        appointment = (await self.db.execute(stmt)).scalar_one_or_none()

        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reschedule this appointment")

        if appointment.status in [AppointmentStatus.CANCELLED.value, AppointmentStatus.COMPLETED.value]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot reschedule a {appointment.status} appointment")

        # 2. Lock old slot
        old_slot_stmt = select(AppointmentSlot).where(AppointmentSlot.id == appointment.slot_id).with_for_update()
        old_slot = (await self.db.execute(old_slot_stmt)).scalar_one()

        # 3. Lock new slot
        new_slot_stmt = select(AppointmentSlot).where(AppointmentSlot.id == new_slot_id).with_for_update()
        new_slot = (await self.db.execute(new_slot_stmt)).scalar_one_or_none()

        if not new_slot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New slot not found")

        now = datetime.now(timezone.utc)
        
        # New slot must be available OR held by this patient
        if new_slot.status not in [SlotStatus.AVAILABLE.value, SlotStatus.HELD.value]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="New slot is not available")
            
        if new_slot.status == SlotStatus.HELD.value and (new_slot.held_by != current_user.id or not new_slot.held_until or new_slot.held_until < now):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New slot is held by someone else")

        # Optional: Patient overlap validation for the new slot
        overlap_stmt = (
            select(Appointment)
            .join(AppointmentSlot, Appointment.slot_id == AppointmentSlot.id)
            .where(
                Appointment.patient_id == current_user.id,
                Appointment.id != appointment.id,
                AppointmentSlot.slot_date == new_slot.slot_date,
                AppointmentSlot.start_time == new_slot.start_time,
                Appointment.status != AppointmentStatus.CANCELLED.value
            )
        )
        overlap = (await self.db.execute(overlap_stmt)).scalar_one_or_none()
        if overlap:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already have an appointment booked for this new date and time.")

        # 4. Perform swaps
        old_slot.status = SlotStatus.AVAILABLE.value
        
        new_slot.status = SlotStatus.BOOKED.value
        new_slot.held_by = None
        new_slot.held_until = None
        
        appointment.slot_id = new_slot.id
        appointment.doctor_id = new_slot.doctor_id

        await self.db.commit()

        # Reload relationships
        await self.db.refresh(appointment)
        
        old_date = old_slot.slot_date.strftime("%Y-%m-%d")
        old_time = old_slot.start_time.strftime("%H:%M")
        send_reschedule_email_task.delay(str(appointment.id), old_date, old_time)
        update_calendar_event_task.delay(str(appointment.id))

        return AppointmentRescheduleResponse(
            id=appointment.id,
            status=appointment.status,
            slot=new_slot,
            previous_slot=old_slot
        )

    async def get_appointment(self, appointment_id: uuid.UUID, current_user: User) -> Appointment:
        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.slot),
                joinedload(Appointment.patient).joinedload(Patient.user),
                joinedload(Appointment.doctor).joinedload(Doctor.user),
                joinedload(Appointment.consultation)
            )
            .where(Appointment.id == appointment_id)
        )
        result = await self.db.execute(stmt)
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

        # Authorization check
        if current_user.role == "patient" and appointment.patient.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this appointment")
        
        if current_user.role == "doctor" and appointment.doctor.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this appointment")

        return appointment
