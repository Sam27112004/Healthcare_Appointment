from datetime import datetime, timezone
import logging
import asyncio
from sqlalchemy import update
from app.celery_app import celery_app
from app.database import celery_session_factory
from app.models.slot import AppointmentSlot

logger = logging.getLogger(__name__)


async def _cleanup_expired_holds_async():
    now = datetime.now(timezone.utc)
    try:
        async with celery_session_factory() as db:
            result = await db.execute(
                update(AppointmentSlot)
                .where(
                    AppointmentSlot.status == "held",
                    AppointmentSlot.held_until < now
                )
                .values(
                    status="available",
                    held_by=None,
                    held_until=None
                )
            )
            await db.commit()
            if result.rowcount > 0:
                logger.info(f"Released {result.rowcount} expired slot holds")
    except Exception as e:
        logger.error(f"Failed to cleanup expired holds: {str(e)}")

@celery_app.task(name="app.appointment.tasks.cleanup_expired_holds")
def cleanup_expired_holds():
    """
    Periodic task (every 60s): Release all expired slot holds.
    Slots in 'held' status with held_until < now() are set back to 'available'.
    """
    asyncio.run(_cleanup_expired_holds_async())
