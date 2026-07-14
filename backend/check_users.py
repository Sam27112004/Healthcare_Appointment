import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    async with engine.begin() as conn:
        res = await conn.execute(text('SELECT role, email FROM "user"'))
        print('USERS:', res.fetchall())

asyncio.run(main())
