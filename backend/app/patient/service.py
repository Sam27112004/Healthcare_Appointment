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

    async def get_patient_appointments(self, user_id: uuid.UUID, page: int = 1, limit: int = 20) -> dict:
        from app.models.appointment import Appointment
        from app.models.user import Doctor
        from app.models.consultation import Consultation, Prescription
        from sqlalchemy import func
        
        patient = await self.get_patient_profile(user_id)
        offset = (page - 1) * limit
        
        # Query total
        total_stmt = select(func.count(Appointment.id)).where(Appointment.patient_id == patient.id)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # Query items
        stmt = (
            select(Appointment)
            .where(Appointment.patient_id == patient.id)
            .options(
                selectinload(Appointment.slot),
                selectinload(Appointment.patient).selectinload(Patient.user),
                selectinload(Appointment.doctor).selectinload(Doctor.user),
                selectinload(Appointment.doctor).selectinload(Doctor.specialization),
                selectinload(Appointment.consultation).selectinload(Consultation.prescription).selectinload(Prescription.medications)
            )
            .order_by(Appointment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        appointments = result.scalars().all()
        
        return {
            "items": list(appointments),
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
