import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.doctor.schemas import DoctorProfile
from app.schemas.common import PaginatedResponse
from app.doctor.service import DoctorService
from app.auth.dependencies import get_db, get_current_user

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("", response_model=PaginatedResponse[DoctorProfile], status_code=status.HTTP_200_OK)
async def list_doctors(
    specialization_id: uuid.UUID | None = Query(None, description="Filter by specialization"),
    search: str | None = Query(None, description="Search by doctor name or specialization"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user) # Requires authentication, but any role is fine
):
    """Search and list doctors with filters."""
    service = DoctorService(db)
    return await service.search_doctors(
        specialization_id=specialization_id, 
        search=search, 
        page=page, 
        limit=limit
    )

@router.get("/{doctor_id}", response_model=DoctorProfile, status_code=status.HTTP_200_OK)
async def get_doctor(
    doctor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user)
):
    """Get a single doctor's profile by ID."""
    service = DoctorService(db)
    doctor = await service.get_doctor_profile(doctor_id)
    return DoctorProfile.model_validate(doctor)
