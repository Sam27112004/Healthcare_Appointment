from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.patient.schemas import PatientProfile, PatientUpdate
from app.patient.service import PatientService
from app.auth.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.appointment.schemas import AppointmentResponse

router = APIRouter(prefix="/patients", tags=["Patient Profile"])

@router.get("/me", response_model=PatientProfile, status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: User = Depends(require_role(["patient"])),
    db: AsyncSession = Depends(get_db)
):
    """Get the current patient's profile."""
    service = PatientService(db)
    return await service.get_patient_profile(current_user.id)

@router.put("/me", response_model=PatientProfile, status_code=status.HTTP_200_OK)
async def update_my_profile(
    update_data: PatientUpdate,
    current_user: User = Depends(require_role(["patient"])),
    db: AsyncSession = Depends(get_db)
):
    """Update the current patient's profile."""
    service = PatientService(db)
    return await service.update_patient_profile(current_user.id, update_data)

@router.get("/me/appointments", response_model=PaginatedResponse[AppointmentResponse], status_code=status.HTTP_200_OK)
async def get_my_appointments(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(require_role(["patient"])),
    db: AsyncSession = Depends(get_db)
):
    """List the current patient's appointments."""
    service = PatientService(db)
    return await service.get_patient_appointments(current_user.id, page, limit)
