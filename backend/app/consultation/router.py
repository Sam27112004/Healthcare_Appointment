import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.consultation.schemas import DoctorDashboardResponse, PreVisitSummaryResponse
from app.consultation.service import ConsultationService
from app.auth.dependencies import get_db, require_role
from app.models.user import User

router = APIRouter(prefix="/doctor", tags=["Consultation"])

@router.get("/dashboard", response_model=DoctorDashboardResponse, status_code=status.HTTP_200_OK)
async def get_dashboard(
    current_user: User = Depends(require_role(["doctor"])),
    db: AsyncSession = Depends(get_db)
):
    """Get the doctor's dashboard data (today's schedule and basic stats)."""
    service = ConsultationService(db)
    return await service.get_doctor_dashboard(current_user.id)

@router.get("/appointments", status_code=status.HTTP_200_OK)
async def get_appointments(
    status_filter: Optional[str] = Query("all", alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(["doctor"])),
    db: AsyncSession = Depends(get_db)
):
    """List the doctor's appointments."""
    service = ConsultationService(db)
    return await service.get_doctor_appointments(current_user.id, status_filter, page, limit)

@router.get("/appointments/{appointment_id}/pre-visit-summary", response_model=PreVisitSummaryResponse, status_code=status.HTTP_200_OK)
async def get_pre_visit_summary(
    appointment_id: uuid.UUID,
    current_user: User = Depends(require_role(["doctor"])),
    db: AsyncSession = Depends(get_db)
):
    """Get the AI-generated pre-visit summary for an appointment."""
    service = ConsultationService(db)
    return await service.get_pre_visit_summary(current_user.id, appointment_id)
