import asyncio
import uuid
from datetime import datetime, timezone
from celery.utils.log import get_task_logger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.celery_app import celery_app
from app.database import async_session_factory
from app.models.appointment import Appointment
from app.models.slot import AppointmentSlot
from app.models.user import User
from app.models.calendar_event import CalendarEvent
from app.config import settings

logger = get_task_logger(__name__)

def _get_google_service(user: User):
    if not user.google_access_token or not user.google_refresh_token:
        return None
        
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/calendar.events']
    )
    return build('calendar', 'v3', credentials=creds)

async def _create_calendar_event(appointment_id: str):
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient).selectinload("user"),
                selectinload(Appointment.doctor).selectinload("user"),
                selectinload(Appointment.slot)
            )
            .where(Appointment.id == uuid.UUID(appointment_id))
        )
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        if not appointment:
            return

        # Prepare event details
        start_datetime = datetime.combine(appointment.slot.slot_date, appointment.slot.start_time).isoformat() + 'Z'
        end_datetime = datetime.combine(appointment.slot.slot_date, appointment.slot.end_time).isoformat() + 'Z'
        
        event_body = {
            'summary': f"Medical Appointment: Dr. {appointment.doctor.user.full_name} and {appointment.patient.user.full_name}",
            'description': f"Symptoms: {appointment.symptoms}\nSeverity: {appointment.symptom_severity}",
            'start': {'dateTime': start_datetime, 'timeZone': 'UTC'},
            'end': {'dateTime': end_datetime, 'timeZone': 'UTC'},
        }

        # Look for existing tracking record
        cal_evt_stmt = select(CalendarEvent).where(CalendarEvent.appointment_id == appointment.id)
        cal_event = (await db.execute(cal_evt_stmt)).scalar_one_or_none()
        
        if not cal_event:
            cal_event = CalendarEvent(appointment_id=appointment.id)
            db.add(cal_event)

        # 1. Create event for Patient
        patient_service = _get_google_service(appointment.patient.user)
        if patient_service:
            try:
                created_event = patient_service.events().insert(calendarId='primary', body=event_body).execute()
                cal_event.patient_event_id = created_event.get('id')
                cal_event.status = 'created'
            except Exception as e:
                logger.error(f"Failed to create patient calendar event: {e}")
                cal_event.last_error = str(e)

        # 2. Create event for Doctor
        doctor_service = _get_google_service(appointment.doctor.user)
        if doctor_service:
            try:
                created_event = doctor_service.events().insert(calendarId='primary', body=event_body).execute()
                cal_event.doctor_event_id = created_event.get('id')
                cal_event.status = 'created'
            except Exception as e:
                logger.error(f"Failed to create doctor calendar event: {e}")
                cal_event.last_error = str(e)

        await db.commit()

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def create_calendar_event_task(self, appointment_id: str):
    try:
        asyncio.run(_create_calendar_event(appointment_id))
    except Exception as exc:
        logger.warning(f"Retrying calendar creation for {appointment_id}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)

async def _update_calendar_event(appointment_id: str):
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient).selectinload("user"),
                selectinload(Appointment.doctor).selectinload("user"),
                selectinload(Appointment.slot)
            )
            .where(Appointment.id == uuid.UUID(appointment_id))
        )
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        cal_evt_stmt = select(CalendarEvent).where(CalendarEvent.appointment_id == uuid.UUID(appointment_id))
        cal_event = (await db.execute(cal_evt_stmt)).scalar_one_or_none()

        if not appointment or not cal_event:
            return

        start_datetime = datetime.combine(appointment.slot.slot_date, appointment.slot.start_time).isoformat() + 'Z'
        end_datetime = datetime.combine(appointment.slot.slot_date, appointment.slot.end_time).isoformat() + 'Z'
        
        event_body = {
            'start': {'dateTime': start_datetime, 'timeZone': 'UTC'},
            'end': {'dateTime': end_datetime, 'timeZone': 'UTC'},
        }

        if cal_event.patient_event_id:
            patient_service = _get_google_service(appointment.patient.user)
            if patient_service:
                try:
                    patient_service.events().patch(calendarId='primary', eventId=cal_event.patient_event_id, body=event_body).execute()
                except Exception as e:
                    logger.error(f"Failed to update patient event: {e}")

        if cal_event.doctor_event_id:
            doctor_service = _get_google_service(appointment.doctor.user)
            if doctor_service:
                try:
                    doctor_service.events().patch(calendarId='primary', eventId=cal_event.doctor_event_id, body=event_body).execute()
                except Exception as e:
                    logger.error(f"Failed to update doctor event: {e}")

        cal_event.status = 'updated'
        cal_event.updated_at = datetime.now(timezone.utc)
        await db.commit()

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def update_calendar_event_task(self, appointment_id: str):
    try:
        asyncio.run(_update_calendar_event(appointment_id))
    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)

async def _delete_calendar_event(appointment_id: str):
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient).selectinload("user"),
                selectinload(Appointment.doctor).selectinload("user")
            )
            .where(Appointment.id == uuid.UUID(appointment_id))
        )
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        cal_evt_stmt = select(CalendarEvent).where(CalendarEvent.appointment_id == uuid.UUID(appointment_id))
        cal_event = (await db.execute(cal_evt_stmt)).scalar_one_or_none()

        if not appointment or not cal_event:
            return

        if cal_event.patient_event_id:
            patient_service = _get_google_service(appointment.patient.user)
            if patient_service:
                try:
                    patient_service.events().delete(calendarId='primary', eventId=cal_event.patient_event_id).execute()
                except Exception as e:
                    logger.error(f"Failed to delete patient event: {e}")

        if cal_event.doctor_event_id:
            doctor_service = _get_google_service(appointment.doctor.user)
            if doctor_service:
                try:
                    doctor_service.events().delete(calendarId='primary', eventId=cal_event.doctor_event_id).execute()
                except Exception as e:
                    logger.error(f"Failed to delete doctor event: {e}")

        cal_event.status = 'deleted'
        cal_event.updated_at = datetime.now(timezone.utc)
        await db.commit()

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def delete_calendar_event_task(self, appointment_id: str):
    try:
        asyncio.run(_delete_calendar_event(appointment_id))
    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)
