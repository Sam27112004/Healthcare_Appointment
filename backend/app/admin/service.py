import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload, joinedload
from app.models.specialization import Specialization
from app.models.user import Doctor, User
from app.admin.schemas import SpecializationCreate, SpecializationUpdate, DoctorCreate, DoctorUpdate
from app.auth.security import get_password_hash
from app.schemas.enums import Role
from app.schemas.common import PaginatedResponse
from app.doctor.schemas import DoctorProfile

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

    # ================= Doctor Management =================

    async def get_doctors(self, page: int = 1, limit: int = 20) -> PaginatedResponse[DoctorProfile]:
        # This differs from the public search_doctors by returning ALL doctors (even inactive ones)
        # Admins need to see inactive ones to reactivate them if needed.
        stmt = select(Doctor).join(User).options(
            selectinload(Doctor.user),
            selectinload(Doctor.specialization)
        )
        count_stmt = select(func.count(Doctor.id)).join(User)

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        doctors = result.scalars().all()
        
        items = [DoctorProfile.model_validate(doc) for doc in doctors]
        return PaginatedResponse.create(items=items, total=total, page=page, limit=limit)

    async def create_doctor(self, data: DoctorCreate) -> Doctor:
        # Check if email exists
        stmt = select(User).where(User.email == data.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Verify specialization exists
        spec_stmt = select(Specialization).where(Specialization.id == data.specialization_id)
        spec = (await self.db.execute(spec_stmt)).scalar_one_or_none()
        if not spec:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization not found")

        # Create user
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role=Role.DOCTOR.value,
            is_active=True
        )
        self.db.add(user)
        await self.db.flush() # flush to get user.id

        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            specialization_id=data.specialization_id,
            qualification=data.qualification,
            experience_years=data.experience_years,
            bio=data.bio,
            consultation_fee=data.consultation_fee
        )
        self.db.add(doctor)
        
        await self.db.commit()
        # Fetch the complete doctor with relationships
        return await self._get_doctor_with_rels(doctor.id)

    async def _get_doctor_with_rels(self, doctor_id: uuid.UUID) -> Doctor:
        stmt = select(Doctor).where(Doctor.id == doctor_id).options(
            selectinload(Doctor.user),
            selectinload(Doctor.specialization)
        )
        result = await self.db.execute(stmt)
        doctor = result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        return doctor

    async def update_doctor(self, doctor_id: uuid.UUID, data: DoctorUpdate) -> Doctor:
        doctor = await self._get_doctor_with_rels(doctor_id)

        # Update User fields
        if data.full_name is not None:
            doctor.user.full_name = data.full_name
        if data.phone is not None:
            doctor.user.phone = data.phone
        if data.is_active is not None:
            doctor.user.is_active = data.is_active

        # Update Doctor fields
        if data.specialization_id is not None:
            spec_stmt = select(Specialization).where(Specialization.id == data.specialization_id)
            spec = (await self.db.execute(spec_stmt)).scalar_one_or_none()
            if not spec:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specialization not found")
            doctor.specialization_id = data.specialization_id

        if data.qualification is not None:
            doctor.qualification = data.qualification
        if data.experience_years is not None:
            doctor.experience_years = data.experience_years
        if data.bio is not None:
            doctor.bio = data.bio
        if data.consultation_fee is not None:
            doctor.consultation_fee = data.consultation_fee

        await self.db.commit()
        return await self._get_doctor_with_rels(doctor_id)

    async def deactivate_doctor(self, doctor_id: uuid.UUID) -> None:
        doctor = await self._get_doctor_with_rels(doctor_id)
        doctor.user.is_active = False
        await self.db.commit()
