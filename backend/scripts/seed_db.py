import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.base import Base
from app.models.user import User, Doctor, Patient
from app.models.specialization import Specialization
from app.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            # Create specializations
            specs = [
                "Cardiology", "Dermatology", "Endocrinology", "Gastroenterology",
                "General Practice", "Neurology", "Orthopedics", "Pediatrics",
                "Psychiatry", "Radiology"
            ]
            spec_objects = {}
            for name in specs:
                spec = Specialization(name=name, description=f"{name} specialist")
                session.add(spec)
                spec_objects[name] = spec
            
            await session.flush() # Flush to get IDs

            # Create Admin User
            admin_user = User(
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                full_name="System Admin",
                role="admin"
            )
            session.add(admin_user)

            # Create Test Doctor
            doctor_user = User(
                email="doctor@example.com",
                hashed_password=pwd_context.hash("doctor123"),
                full_name="Dr. Jane Smith",
                role="doctor"
            )
            session.add(doctor_user)
            await session.flush()

            doctor_profile = Doctor(
                user_id=doctor_user.id,
                specialization_id=spec_objects["Cardiology"].id,
                qualification="MD, FACC",
                experience_years=10,
                bio="Experienced cardiologist specializing in heart failure.",
                consultation_fee=150.00
            )
            session.add(doctor_profile)

            # Create Test Patient
            patient_user = User(
                email="patient@example.com",
                hashed_password=pwd_context.hash("patient123"),
                full_name="John Doe",
                role="patient"
            )
            session.add(patient_user)
            await session.flush()

            patient_profile = Patient(
                user_id=patient_user.id,
                gender="Male",
                blood_group="O+"
            )
            session.add(patient_profile)

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
