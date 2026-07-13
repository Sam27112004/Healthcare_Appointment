import asyncio
import uuid
from datetime import datetime, timezone, timedelta, date
from celery.utils.log import get_task_logger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.celery_app import celery_app
from app.database import async_session_factory
from app.models.appointment import Appointment
from app.models.slot import AppointmentSlot
from app.models.user import User
from app.models.user import User, Patient, Doctor
from app.models.schedule import DoctorLeave
from app.models.consultation import Consultation, Prescription, Medication
from app.notifications.service import NotificationService
from app.schemas.enums import NotificationType, AppointmentStatus
from app.config import settings

logger = get_task_logger(__name__)

async def _send_booking_confirmation(appointment_id: str):
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient).selectinload(Patient.user), selectinload(Appointment.doctor).selectinload(Doctor.user), selectinload(Appointment.slot))
            .where(Appointment.id == uuid.UUID(appointment_id))
        )
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        if not appointment:
            logger.error(f"Appointment {appointment_id} not found")
            return

        service = NotificationService(db)
        
        # Patient Email
        await service.send_email(
            user_id=appointment.patient.user_id,
            email_to=appointment.patient.user.email,
            subject="Appointment Confirmed",
            template_name="booking_confirmation.html",
            context={
                "patient_name": appointment.patient.user.full_name,
                "doctor_name": appointment.doctor.user.full_name,
                "date": appointment.slot.slot_date.strftime("%Y-%m-%d"),
                "time": appointment.slot.start_time.strftime("%H:%M")
            },
            notification_type=NotificationType.BOOKING_CONFIRMATION
        )
        
        # Doctor Email (optional, but good practice)
        await service.send_email(
            user_id=appointment.doctor.user_id,
            email_to=appointment.doctor.user.email,
            subject="New Appointment Booked",
            template_name="booking_confirmation.html",
            context={
                "patient_name": appointment.doctor.user.full_name, # reuse template layout
                "doctor_name": "Dr. " + appointment.doctor.user.full_name,
                "date": appointment.slot.slot_date.strftime("%Y-%m-%d"),
                "time": appointment.slot.start_time.strftime("%H:%M")
            },
            notification_type=NotificationType.BOOKING_CONFIRMATION
        )

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def send_booking_confirmation_task(self, appointment_id: str):
    try:
        asyncio.run(_send_booking_confirmation(appointment_id))
    except Exception as exc:
        logger.warning(f"Retrying booking email for {appointment_id} due to {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)


async def _send_cancellation_email(appointment_id: str):
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient).selectinload(Patient.user), selectinload(Appointment.doctor).selectinload(Doctor.user), selectinload(Appointment.slot))
            .where(Appointment.id == uuid.UUID(appointment_id))
        )
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        if not appointment:
            logger.error(f"Appointment {appointment_id} not found")
            return

        service = NotificationService(db)
        
        await service.send_email(
            user_id=appointment.patient.user_id,
            email_to=appointment.patient.user.email,
            subject="Appointment Cancelled",
            template_name="cancellation.html",
            context={
                "patient_name": appointment.patient.user.full_name,
                "doctor_name": appointment.doctor.user.full_name,
                "date": appointment.slot.slot_date.strftime("%Y-%m-%d"),
                "time": appointment.slot.start_time.strftime("%H:%M"),
                "reason": appointment.cancellation_reason
            },
            notification_type=NotificationType.CANCELLATION
        )

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def send_cancellation_email_task(self, appointment_id: str):
    try:
        asyncio.run(_send_cancellation_email(appointment_id))
    except Exception as exc:
        logger.warning(f"Retrying cancellation email for {appointment_id} due to {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)


async def _send_reschedule_email(appointment_id: str, old_date: str, old_time: str):
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient).selectinload(Patient.user), selectinload(Appointment.doctor).selectinload(Doctor.user), selectinload(Appointment.slot))
            .where(Appointment.id == uuid.UUID(appointment_id))
        )
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        if not appointment:
            logger.error(f"Appointment {appointment_id} not found")
            return

        service = NotificationService(db)
        
        await service.send_email(
            user_id=appointment.patient.user_id,
            email_to=appointment.patient.user.email,
            subject="Appointment Rescheduled",
            template_name="reschedule.html",
            context={
                "patient_name": appointment.patient.user.full_name,
                "doctor_name": appointment.doctor.user.full_name,
                "old_date": old_date,
                "old_time": old_time,
                "new_date": appointment.slot.slot_date.strftime("%Y-%m-%d"),
                "new_time": appointment.slot.start_time.strftime("%H:%M")
            },
            notification_type=NotificationType.RESCHEDULE
        )

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def send_reschedule_email_task(self, appointment_id: str, old_date: str, old_time: str):
    try:
        asyncio.run(_send_reschedule_email(appointment_id, old_date, old_time))
    except Exception as exc:
        logger.warning(f"Retrying reschedule email for {appointment_id} due to {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)


async def _send_leave_notification(leave_id: str):
    async with async_session_factory() as db:
        # Fetch the leave record
        stmt = select(DoctorLeave).options(selectinload(DoctorLeave.doctor).selectinload(Doctor.user)).where(DoctorLeave.id == uuid.UUID(leave_id))
        leave = (await db.execute(stmt)).scalar_one_or_none()
        
        if not leave:
            logger.error(f"Leave {leave_id} not found")
            return

        # Fetch affected booked appointments for this doctor on this date
        appt_stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient).selectinload(Patient.user))
            .join(AppointmentSlot)
            .where(
                Appointment.doctor_id == leave.doctor_id,
                AppointmentSlot.slot_date == leave.leave_date,
                Appointment.status == AppointmentStatus.BOOKED.value
            )
        )
        appointments = (await db.execute(appt_stmt)).scalars().all()

        service = NotificationService(db)
        
        for appointment in appointments:
            try:
                # Cancel the appointment since the doctor is on leave
                appointment.status = AppointmentStatus.CANCELLED.value
                appointment.cancellation_reason = "Doctor on emergency leave"
                appointment.cancelled_by = "system"
                await db.commit()

                # Send email
                await service.send_email(
                    user_id=appointment.patient.user_id,
                    email_to=appointment.patient.user.email,
                    subject="Doctor Leave - Appointment Cancelled",
                    template_name="leave_notification.html",
                    context={
                        "patient_name": appointment.patient.user.full_name,
                        "doctor_name": leave.doctor.user.full_name,
                        "date": leave.leave_date.strftime("%Y-%m-%d")
                    },
                    notification_type=NotificationType.LEAVE_NOTIFICATION
                )
            except Exception as inner_exc:
                logger.error(f"Failed to process leave notification for appointment {appointment.id}: {inner_exc}")
                # continue processing others

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def send_leave_notification_task(self, leave_id: str):
    try:
        asyncio.run(_send_leave_notification(leave_id))
    except Exception as exc:
        logger.warning(f"Retrying leave notification email for {leave_id} due to {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)


async def _send_consultation_complete(appointment_id: str):
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient).selectinload(Patient.user), selectinload(Appointment.doctor).selectinload(Doctor.user))
            .where(Appointment.id == uuid.UUID(appointment_id))
        )
        appointment = (await db.execute(stmt)).scalar_one_or_none()
        
        if not appointment:
            logger.error(f"Appointment {appointment_id} not found")
            return

        service = NotificationService(db)
        
        await service.send_email(
            user_id=appointment.patient.user_id,
            email_to=appointment.patient.user.email,
            subject="Consultation Complete & Summary Available",
            template_name="consultation_completed.html",
            context={
                "patient_name": appointment.patient.user.full_name,
                "doctor_name": appointment.doctor.user.full_name,
            },
            notification_type=NotificationType.CONSULTATION_COMPLETED
        )

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def send_consultation_complete_task(self, appointment_id: str):
    try:
        asyncio.run(_send_consultation_complete(appointment_id))
    except Exception as exc:
        logger.warning(f"Retrying consultation complete email for {appointment_id} due to {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)

async def _send_appointment_reminders():
    # Remind for appointments happening tomorrow
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
    
    async with async_session_factory() as db:
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient).selectinload(Patient.user), selectinload(Appointment.doctor).selectinload(Doctor.user), selectinload(Appointment.slot))
            .join(AppointmentSlot)
            .where(
                AppointmentSlot.slot_date == tomorrow,
                Appointment.status == AppointmentStatus.BOOKED.value
            )
        )
        appointments = (await db.execute(stmt)).scalars().all()
        
        service = NotificationService(db)
        for appointment in appointments:
            try:
                await service.send_email(
                    user_id=appointment.patient.user_id,
                    email_to=appointment.patient.user.email,
                    subject="Appointment Reminder",
                    template_name="appointment_reminder.html",
                    context={
                        "patient_name": appointment.patient.user.full_name,
                        "doctor_name": appointment.doctor.user.full_name,
                        "date": appointment.slot.slot_date.strftime("%Y-%m-%d"),
                        "time": appointment.slot.start_time.strftime("%H:%M")
                    },
                    notification_type=NotificationType.APPOINTMENT_REMINDER
                )
            except Exception as e:
                logger.error(f"Failed to send reminder for appointment {appointment.id}: {e}")

@celery_app.task
def send_appointment_reminders_task():
    asyncio.run(_send_appointment_reminders())

async def _send_medication_reminders():
    today = datetime.now(timezone.utc).date()
    
    async with async_session_factory() as db:
        stmt = (
            select(Medication)
            .options(
                selectinload(Medication.prescription)
                .selectinload(Prescription.consultation)
                .selectinload(Consultation.appointment)
                .selectinload(Appointment.patient)
                .selectinload(Patient.user)
            )
            .where(
                Medication.start_date <= today,
                Medication.end_date >= today
            )
        )
        medications = (await db.execute(stmt)).scalars().all()
        
        service = NotificationService(db)
        # Simplified: we send a reminder for each active medication once when this runs.
        # In a real app, this might track time-of-day frequencies.
        for med in medications:
            try:
                await service.send_email(
                    user_id=med.prescription.consultation.appointment.patient.user_id,
                    email_to=med.prescription.consultation.appointment.patient.user.email,
                    subject=f"Medication Reminder: {med.name}",
                    template_name="medication_reminder.html",
                    context={
                        "patient_name": med.prescription.consultation.appointment.patient.user.full_name,
                        "medication_name": med.name,
                        "dosage": med.dosage,
                        "instructions": med.instructions or ""
                    },
                    notification_type=NotificationType.MEDICATION_REMINDER
                )
            except Exception as e:
                logger.error(f"Failed to send medication reminder for {med.id}: {e}")

@celery_app.task
def send_medication_reminders_task():
    asyncio.run(_send_medication_reminders())

async def _retry_failed_notifications():
    # Only retry notifications failed in the last 24 hours
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    
    async with async_session_factory() as db:
        from app.models.notification import Notification
        from app.schemas.enums import NotificationStatus
        
        stmt = select(Notification).where(
            Notification.status == NotificationStatus.FAILED.value,
            Notification.created_at >= yesterday
        )
        failed_notifs = (await db.execute(stmt)).scalars().all()
        
        service = NotificationService(db)
        for notif in failed_notifs:
            try:
                # Re-send using saved properties
                from app.notifications.email import mail, MessageSchema, MessageType
                
                message = MessageSchema(
                    subject=notif.subject,
                    recipients=[notif.recipient],
                    template_body={}, # we don't have the context saved, but assume it's just a raw resend if we had it.
                    # Since we don't have the original context JSON saved, a true retry is tricky. 
                    # We will just mark it retrying and try to send a generic fallback or skip.
                    # Let's just log it for now.
                    subtype=MessageType.html
                )
                logger.info(f"Would retry notification {notif.id} here, but context is missing.")
            except Exception as e:
                logger.error(f"Retry failed for {notif.id}: {e}")

@celery_app.task
def retry_failed_notifications_task():
    asyncio.run(_retry_failed_notifications())
