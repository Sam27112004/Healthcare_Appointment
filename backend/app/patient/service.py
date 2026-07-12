from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User, Patient
from app.patient.schemas import PatientUpdate
import uuid

class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_patient_profile(self, user_id: uuid.UUID) -> Patient:
        stmt = (
            select(Patient)
            .where(Patient.user_id == user_id)
            .options(selectinload(Patient.user))
        )
        result = await self.db.execute(stmt)
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
            
        return patient

    async def update_patient_profile(self, user_id: uuid.UUID, update_data: PatientUpdate) -> Patient:
        patient = await self.get_patient_profile(user_id)
        
        # Update user fields if provided
        if update_data.full_name is not None:
            patient.user.full_name = update_data.full_name
        if update_data.phone is not None:
            patient.user.phone = update_data.phone
            
        # Update patient fields
        if update_data.date_of_birth is not None:
            patient.date_of_birth = update_data.date_of_birth
        if update_data.gender is not None:
            patient.gender = update_data.gender
        if update_data.blood_group is not None:
            patient.blood_group = update_data.blood_group
        if update_data.address is not None:
            patient.address = update_data.address
        if update_data.medical_history is not None:
            patient.medical_history = update_data.medical_history
            
        await self.db.commit()
        await self.db.refresh(patient)
        return patient
