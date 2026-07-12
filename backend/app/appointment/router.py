import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.appointment.schemas import (
    SlotHoldRequest, SlotHoldResponse, AppointmentCreate, AppointmentResponse,
    AppointmentCancelRequest, AppointmentCancelResponse, AppointmentRescheduleRequest, AppointmentRescheduleResponse
)
from app.appointment.service import AppointmentService
from app.auth.dependencies import get_db, require_role
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/hold", response_model=SlotHoldResponse, status_code=status.HTTP_200_OK)
async def hold_appointment_slot(
    data: SlotHoldRequest,
    current_user: User = Depends(require_role(["patient"])),
    db: AsyncSession = Depends(get_db)
):
    """Hold a slot temporarily while the patient fills the symptom form."""
    service = AppointmentService(db)
    return await service.hold_slot(current_user.id, data.slot_id)

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_role(["patient"])),
    db: AsyncSession = Depends(get_db)
):
    """Confirm a booking. Slot must be held by this patient."""
    service = AppointmentService(db)
    return await service.book_appointment(current_user.id, data)

@router.post("/{appointment_id}/cancel", response_model=AppointmentCancelResponse, status_code=status.HTTP_200_OK)
async def cancel_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentCancelRequest,
    current_user: User = Depends(require_role(["patient", "doctor", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an upcoming appointment."""
    service = AppointmentService(db)
    return await service.cancel_appointment(appointment_id, current_user, data.reason)

@router.post("/{appointment_id}/reschedule", response_model=AppointmentRescheduleResponse, status_code=status.HTTP_200_OK)
async def reschedule_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentRescheduleRequest,
    current_user: User = Depends(require_role(["patient"])),
    db: AsyncSession = Depends(get_db)
):
    """Reschedule to a different slot."""
    service = AppointmentService(db)
    return await service.reschedule_appointment(appointment_id, current_user, data.new_slot_id)
