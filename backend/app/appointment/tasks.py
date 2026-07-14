from datetime import datetime, timezone
import logging
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import engine
from app.models.slot import AppointmentSlot

logger = logging.getLogger(__name__)

@celery_app.task(name="app.appointment.tasks.cleanup_expired_holds")
def cleanup_expired_holds():
    """
    Periodic task (every 60s): Release all expired slot holds.
    Slots in 'held' status with held_until < now() are set back to 'available'.
    """
    now = datetime.now(timezone.utc)
    try:
        with Session(engine) as db:
            expired_count = db.execute(
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
            db.commit()
            if expired_count.rowcount > 0:
                logger.info(f"Released {expired_count.rowcount} expired slot holds")
    except Exception as e:
        logger.error(f"Failed to cleanup expired holds: {str(e)}")
