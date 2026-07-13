from enum import Enum

class Role(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class AppointmentStatus(str, Enum):
    BOOKED = "booked"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NOSHOW = "no_show"

class SlotStatus(str, Enum):
    AVAILABLE = "available"
    HELD = "held"
    BOOKED = "booked"
    BLOCKED = "blocked"

class NotificationType(str, Enum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    APPOINTMENT_REMINDER = "appointment_reminder"
    CANCELLATION = "cancellation"
    RESCHEDULE = "reschedule"
    MEDICATION_REMINDER = "medication_reminder"
    LEAVE_NOTIFICATION = "leave_notification"
    CONSULTATION_COMPLETE = "consultation_complete"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"

class CalendarEventStatus(str, Enum):
    PENDING = "pending"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    FAILED = "failed"

class AIStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
