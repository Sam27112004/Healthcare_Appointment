import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.slot import AppointmentSlot
from app.appointment.schemas import SlotHoldResponse
from app.schemas.enums import SlotStatus

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
