import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload, joinedload
from app.models.user import Doctor, User
from app.models.specialization import Specialization
from app.doctor.schemas import DoctorProfile
from app.schemas.common import PaginatedResponse

class DoctorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_doctor_profile(self, doctor_id: uuid.UUID) -> Doctor:
        stmt = (
            select(Doctor)
            .where(Doctor.id == doctor_id)
            .options(
                joinedload(Doctor.user),
                joinedload(Doctor.specialization)
            )
        )
        result = await self.db.execute(stmt)
        doctor = result.scalar_one_or_none()
        
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
            
        return doctor

    async def search_doctors(
        self, 
        specialization_id: uuid.UUID | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse[DoctorProfile]:
        
        # Base query
        stmt = select(Doctor).join(User).options(
            selectinload(Doctor.user),
            selectinload(Doctor.specialization)
        ).where(User.is_active == True)
        
        count_stmt = select(func.count(Doctor.id)).join(User).where(User.is_active == True)

        # Apply filters
        if specialization_id:
            stmt = stmt.where(Doctor.specialization_id == specialization_id)
            count_stmt = count_stmt.where(Doctor.specialization_id == specialization_id)
            
        if search:
            search_pattern = f"%{search}%"
            # Search by doctor name or specialization name
            stmt = stmt.join(Specialization, isouter=True).where(
                or_(
                    User.full_name.ilike(search_pattern),
                    Specialization.name.ilike(search_pattern)
                )
            )
            count_stmt = count_stmt.join(Specialization, isouter=True).where(
                or_(
                    User.full_name.ilike(search_pattern),
                    Specialization.name.ilike(search_pattern)
                )
            )

        # Execute count
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        # Execute query
        result = await self.db.execute(stmt)
        doctors = result.scalars().all()
        
        # We manually map to Pydantic here for the PaginatedResponse generic since ORM 
        # objects can cause issues if lazy loads trigger later outside session context.
        # But `from_attributes=True` handles this natively if relationships are eager loaded.
        items = [DoctorProfile.model_validate(doc) for doc in doctors]

        return PaginatedResponse.create(items=items, total=total, page=page, limit=limit)
