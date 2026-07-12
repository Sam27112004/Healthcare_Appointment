from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.appointment.schemas import SlotHoldRequest, SlotHoldResponse
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
