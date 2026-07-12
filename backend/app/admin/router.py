import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.admin.schemas import SpecializationCreate, SpecializationUpdate, SpecializationResponse, DoctorCreate, DoctorUpdate
from app.admin.service import AdminService
from app.auth.dependencies import get_db, require_role
from app.schemas.common import PaginatedResponse
from app.doctor.schemas import DoctorProfile

router = APIRouter(prefix="/admin", tags=["Admin"])

# ================= Specializations =================

@router.get("/specializations", response_model=List[SpecializationResponse], status_code=status.HTTP_200_OK)
async def list_specializations(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """List all specializations (Admin only)."""
    service = AdminService(db)
    return await service.get_specializations()

@router.post("/specializations", response_model=SpecializationResponse, status_code=status.HTTP_201_CREATED)
async def create_specialization(
    data: SpecializationCreate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """Create a new specialization."""
    service = AdminService(db)
    return await service.create_specialization(data)

@router.put("/specializations/{spec_id}", response_model=SpecializationResponse, status_code=status.HTTP_200_OK)
async def update_specialization(
    spec_id: uuid.UUID,
    data: SpecializationUpdate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """Update an existing specialization."""
    service = AdminService(db)
    return await service.update_specialization(spec_id, data)

@router.delete("/specializations/{spec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specialization(
    spec_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """Delete a specialization. Fails if doctors are assigned to it."""
    service = AdminService(db)
    await service.delete_specialization(spec_id)

# ================= Doctors =================

@router.get("/doctors", response_model=PaginatedResponse[DoctorProfile], status_code=status.HTTP_200_OK)
async def list_admin_doctors(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """List all doctors including inactive ones (Admin only)."""
    service = AdminService(db)
    return await service.get_doctors(page=page, limit=limit)

@router.post("/doctors", response_model=DoctorProfile, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    data: DoctorCreate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """Create a new doctor profile and user account."""
    service = AdminService(db)
    doctor = await service.create_doctor(data)
    return DoctorProfile.model_validate(doctor)

@router.put("/doctors/{doctor_id}", response_model=DoctorProfile, status_code=status.HTTP_200_OK)
async def update_doctor(
    doctor_id: uuid.UUID,
    data: DoctorUpdate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """Update a doctor's profile or user details."""
    service = AdminService(db)
    doctor = await service.update_doctor(doctor_id, data)
    return DoctorProfile.model_validate(doctor)

@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_doctor(
    doctor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["admin"]))
):
    """Deactivate a doctor (soft delete)."""
    service = AdminService(db)
    await service.deactivate_doctor(doctor_id)
