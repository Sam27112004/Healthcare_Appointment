import asyncio
import uuid
from celery.utils.log import get_task_logger
from sqlalchemy.future import select
from app.celery_app import celery_app
from app.database import celery_session_factory
from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.ai.service import AIService
from app.config import settings

logger = get_task_logger(__name__)

async def _generate_pre_visit_summary(appointment_id: str):
    async with celery_session_factory() as db:
        # Fetch appointment
        stmt = select(Appointment).where(Appointment.id == uuid.UUID(appointment_id))
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        if not appointment:
            logger.error(f"Appointment {appointment_id} not found")
            return
            
        if not appointment.symptoms:
            logger.info(f"No symptoms for appointment {appointment_id}")
            appointment.ai_pre_visit_status = "skipped"
            await db.commit()
            return

        service = AIService()
        try:
            summary = await service.get_pre_visit_summary(appointment.symptoms)
            appointment.ai_pre_visit_summary = summary.model_dump()
            appointment.ai_pre_visit_status = "completed"
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            raise e

        await db.commit()

async def _apply_pre_visit_fallback(appointment_id: str):
    async with celery_session_factory() as db:
        stmt = select(Appointment).where(Appointment.id == uuid.UUID(appointment_id))
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        if appointment:
            appointment.ai_pre_visit_status = "failed"
            appointment.ai_pre_visit_summary = {
                "urgency_level": "Unknown",
                "chief_complaint": appointment.symptoms or "None provided",
                "suggested_questions": ["Please elaborate on your symptoms."]
            }
            await db.commit()

@celery_app.task(bind=True, max_retries=1, acks_late=True)
def generate_pre_visit_summary_task(self, appointment_id: str):
    try:
        asyncio.run(_generate_pre_visit_summary(appointment_id))
    except Exception as exc:
        logger.warning(f"Task failed for appointment {appointment_id} due to {exc}")
        try:
            self.retry(exc=exc, countdown=5)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for {appointment_id}. Applying fallback.")
            asyncio.run(_apply_pre_visit_fallback(appointment_id))

async def _generate_post_visit_summary(appointment_id: str):
    async with celery_session_factory() as db:
        # Fetch consultation via appointment
        stmt = select(Appointment).where(Appointment.id == uuid.UUID(appointment_id))
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        if not appointment:
            logger.error(f"Appointment {appointment_id} not found")
            return

        # Fetch consultation specifically (ensure it exists)
        cons_stmt = select(Consultation).where(Consultation.appointment_id == uuid.UUID(appointment_id))
        consultation = (await db.execute(cons_stmt)).scalar_one_or_none()

        if not consultation or not consultation.notes:
            logger.info(f"No consultation notes for appointment {appointment_id}")
            appointment.ai_post_visit_status = "skipped"
            await db.commit()
            return

        service = AIService()
        try:
            summary = await service.get_post_visit_summary(consultation.notes)
            appointment.ai_post_visit_summary = summary.model_dump()
            appointment.ai_post_visit_status = "completed"
        except Exception as e:
            logger.error(f"AI post-visit generation failed: {str(e)}")
            raise e

        await db.commit()

async def _apply_post_visit_fallback(appointment_id: str):
    async with celery_session_factory() as db:
        stmt = select(Appointment).where(Appointment.id == uuid.UUID(appointment_id))
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        if appointment:
            appointment.ai_post_visit_status = "failed"
            appointment.ai_post_visit_summary = {
                "patient_summary": "We were unable to generate an AI summary for your visit at this time.",
                "medication_schedule": [],
                "follow_up_instructions": "Please refer to your doctor's instructions."
            }
            await db.commit()

@celery_app.task(bind=True, max_retries=1, acks_late=True)
def generate_post_visit_summary_task(self, appointment_id: str):
    try:
        asyncio.run(_generate_post_visit_summary(appointment_id))
    except Exception as exc:
        logger.warning(f"Post-visit task failed for {appointment_id} due to {exc}")
        try:
            self.retry(exc=exc, countdown=5)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for {appointment_id}. Applying fallback.")
            asyncio.run(_apply_post_visit_fallback(appointment_id))
