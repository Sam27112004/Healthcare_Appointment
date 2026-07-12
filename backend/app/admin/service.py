import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.specialization import Specialization
from app.models.user import Doctor
from app.admin.schemas import SpecializationCreate, SpecializationUpdate

class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ================= Specialization Management =================

    async def get_specializations(self) -> list[Specialization]:
        stmt = select(Specialization)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_specialization(self, spec_id: uuid.UUID) -> Specialization:
        stmt = select(Specialization).where(Specialization.id == spec_id)
        result = await self.db.execute(stmt)
        spec = result.scalar_one_or_none()
        if not spec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found")
        return spec

    async def create_specialization(self, data: SpecializationCreate) -> Specialization:
        # Check uniqueness of name
        stmt = select(Specialization).where(func.lower(Specialization.name) == data.name.lower())
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization with this name already exists")
            
        spec = Specialization(
            name=data.name,
            description=data.description
        )
        self.db.add(spec)
        await self.db.commit()
        await self.db.refresh(spec)
        return spec

    async def update_specialization(self, spec_id: uuid.UUID, data: SpecializationUpdate) -> Specialization:
        spec = await self.get_specialization(spec_id)
        
        if data.name is not None:
            # Check uniqueness of new name
            if data.name.lower() != spec.name.lower():
                stmt = select(Specialization).where(func.lower(Specialization.name) == data.name.lower())
                existing = (await self.db.execute(stmt)).scalar_one_or_none()
                if existing:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization with this name already exists")
            spec.name = data.name
            
        if data.description is not None:
            spec.description = data.description
            
        await self.db.commit()
        await self.db.refresh(spec)
        return spec

    async def delete_specialization(self, spec_id: uuid.UUID) -> None:
        spec = await self.get_specialization(spec_id)
        
        # Guard: check if any doctors are currently assigned to this specialization
        stmt = select(Doctor).where(Doctor.specialization_id == spec_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot delete specialization that is assigned to one or more doctors"
            )
            
        await self.db.delete(spec)
        await self.db.commit()
