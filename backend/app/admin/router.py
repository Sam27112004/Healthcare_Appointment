import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.admin.schemas import SpecializationCreate, SpecializationUpdate, SpecializationResponse
from app.admin.service import AdminService
from app.auth.dependencies import get_db, require_role

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
