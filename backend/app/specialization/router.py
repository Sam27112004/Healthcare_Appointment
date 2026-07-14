from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.admin.schemas import SpecializationResponse
from app.admin.service import AdminService
from app.auth.dependencies import get_db, get_current_user

router = APIRouter(prefix="/specializations", tags=["Specializations"])

@router.get("", response_model=List[SpecializationResponse], status_code=status.HTTP_200_OK)
async def list_specializations(
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user)
):
    """List all specializations for dropdowns (Authenticated)."""
    service = AdminService(db)
    return await service.get_specializations()
