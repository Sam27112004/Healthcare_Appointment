import asyncio
from app.database import async_session_maker
from app.models.appointment import Appointment
from sqlalchemy import select

async def main():
    async with async_session_maker() as session:
        res = await session.execute(select(Appointment))
        appts = res.scalars().all()
        print('TOTAL APPTS:', len(appts))
        for a in appts:
            print(a.id, a.doctor_id, a.patient_id, a.status, a.ai_pre_visit_status)

asyncio.run(main())
