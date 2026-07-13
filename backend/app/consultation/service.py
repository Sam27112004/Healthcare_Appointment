import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from app.models.appointment import Appointment
from app.models.slot import AppointmentSlot
from app.models.user import User
from app.consultation.schemas import DoctorDashboardResponse, PreVisitSummaryResponse
from app.schemas.enums import AppointmentStatus, Role

class ConsultationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_doctor_dashboard(self, doctor_id: uuid.UUID) -> DoctorDashboardResponse:
        today = datetime.now(timezone.utc).date()

        # 1. Fetch today's appointments
        today_stmt = (
            select(Appointment)
            .options(selectinload(Appointment.slot))
            .join(AppointmentSlot)
            .where(
                Appointment.doctor_id == doctor_id,
                AppointmentSlot.slot_date == today,
                Appointment.status != AppointmentStatus.CANCELLED.value
            )
            .order_by(AppointmentSlot.start_time)
        )
        today_appointments = (await self.db.execute(today_stmt)).scalars().all()

        # 2. Stats
        completed_today = sum(1 for a in today_appointments if a.status == AppointmentStatus.COMPLETED.value)
        pending_today = sum(1 for a in today_appointments if a.status == AppointmentStatus.BOOKED.value)

        # 3. Upcoming count (future appointments)
        upcoming_stmt = (
            select(func.count(Appointment.id))
            .join(AppointmentSlot)
            .where(
                Appointment.doctor_id == doctor_id,
                AppointmentSlot.slot_date > today,
                Appointment.status == AppointmentStatus.BOOKED.value
            )
        )
        upcoming_count = (await self.db.execute(upcoming_stmt)).scalar() or 0

        return DoctorDashboardResponse(
            today_appointments=list(today_appointments),
            upcoming_count=upcoming_count,
            completed_today=completed_today,
            pending_today=pending_today
        )

    async def get_doctor_appointments(self, doctor_id: uuid.UUID, status_filter: str | None, page: int, limit: int):
        offset = (page - 1) * limit
        
        stmt = select(Appointment).options(selectinload(Appointment.slot)).join(AppointmentSlot).where(Appointment.doctor_id == doctor_id)
        
        if status_filter and status_filter.lower() != "all":
            stmt = stmt.where(Appointment.status == status_filter.lower())
            
        stmt = stmt.order_by(AppointmentSlot.slot_date.desc(), AppointmentSlot.start_time.desc())
        
        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0
        
        # Paginate
        stmt = stmt.offset(offset).limit(limit)
        items = (await self.db.execute(stmt)).scalars().all()
        
        pages = (total + limit - 1) // limit
        
        return {
            "items": list(items),
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }

    async def get_pre_visit_summary(self, doctor_id: uuid.UUID, appointment_id: uuid.UUID) -> PreVisitSummaryResponse:
        stmt = select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.doctor_id == doctor_id
        )
        appointment = (await self.db.execute(stmt)).scalar_one_or_none()

        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found or not assigned to you")

        if appointment.ai_pre_visit_status != "completed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pre-visit summary is not ready yet. Status: {appointment.ai_pre_visit_status}")

        return PreVisitSummaryResponse(
            appointment_id=appointment.id,
            status=appointment.ai_pre_visit_status,
            summary=appointment.ai_pre_visit_summary or {}
        )
