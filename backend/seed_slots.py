import asyncio
import uuid
from datetime import date, timedelta
from app.database import async_session_factory
from app.admin.service import AdminService
from app.models.user import Doctor
from sqlalchemy.future import select

async def seed_slots():
    async with async_session_factory() as db:
        service = AdminService(db)
        
        # Get all doctors
        result = await db.execute(select(Doctor))
        doctors = result.scalars().all()
        
        if not doctors:
            print("No doctors found.")
            return

        for doc in doctors:
            print(f"Generating slots for Doctor ID: {doc.id}")
            start_date = date.today()
            end_date = start_date + timedelta(days=7)
            
            # Create dummy schedule if it doesn't exist
            # Just create Mon-Fri 09:00 to 17:00
            from app.admin.schemas import ScheduleCreate
            from datetime import time
            
            for day in range(1, 6): # 1=Mon, 5=Fri
                try:
                    await service.create_schedule(doc.id, ScheduleCreate(
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        slot_duration=30
                    ))
                except Exception as e:
                    pass # Ignore if already exists
            
            slots_created = await service.generate_slots(doc.id, start_date, end_date)
            print(f"Generated {slots_created} slots for doctor {doc.id}.")

if __name__ == "__main__":
    asyncio.run(seed_slots())
