# System Design & Architecture Write-up

This document outlines the architectural decisions and problem-solving approaches used to fulfill the requirements of the Healthcare Appointment & Follow-up Manager. The system is designed to be highly concurrent, reliable, and strictly role-based.

## 1. Concurrency & Slot Management
### Double-Booking Prevention
In a multi-user healthcare platform, double-booking is a critical edge case. To prevent two patients from booking the same appointment slot simultaneously, we implemented **Database Row-Level Locking**.
Whenever a slot's status is mutated (e.g., from `available` to `booked`), the backend explicitly issues a `SELECT FOR UPDATE` query. This acquires an exclusive lock on the specific `AppointmentSlot` row in PostgreSQL. If a concurrent request attempts to modify the same slot, it must wait until the first transaction commits or rolls back, effectively eliminating any race conditions.

### Slot Hold Mechanism
To ensure a smooth user experience, patients are granted a 10-minute window to fill out their symptom form after selecting a time slot. 
When a slot is selected, it transitions to a `held` state with a `held_until` timestamp. During this time, the slot is invisible to other patients. 
To prevent stale holds from permanently blocking the calendar (e.g., if a user abandons the page), a **Celery Beat background task** runs every 60 seconds (`cleanup_expired_holds`). This task scans the database for slots where `held_until < NOW()` and reverts their status back to `available`.

## 2. Doctor Leave & Conflict Handling
Doctors may occasionally take emergency or planned leave. When an admin marks a doctor as on leave for a specific date, the system immediately records a `DoctorLeave` entry. 
To handle conflicts with already-booked appointments on that date:
1. The API transaction strictly persists the leave record.
2. After the database commit, a `send_leave_notification_task` is dispatched asynchronously to Celery.
3. This background task iterates over all `booked` appointments for that doctor on the specified date, updates their status to `cancelled` with the reason "Doctor on emergency leave", and dispatches cancellation emails to the affected patients.
This asynchronous approach ensures the admin API responds instantly without waiting for dozens of database updates and emails to be sent.

## 3. Reliability & Failure Handling
### Notification Reliability
Email and calendar integrations rely on third-party APIs which can experience downtime or rate limiting. 
To guarantee reliability, all external communications are delegated to **Celery asynchronous tasks**. 
- Tasks are configured with `acks_late=True` so they are re-queued if the Celery worker crashes mid-execution.
- We utilize an exponential backoff retry strategy (`max_retries=3, countdown=2 ** retries`). If an email or Google Calendar API request fails, it is automatically retried later.
- If a notification completely exhausts its retries, it is logged, and a periodic `retry_failed_notifications_task` ensures administrators can audit and manually re-trigger failed dispatches.

### LLM Prompt Quality and Failure Handling
The system leverages Google Gemini for generating pre-visit symptom summaries and post-visit clinical summaries. 
**Prompts:**
- **Pre-visit:** The LLM is instructed to strictly return JSON containing `urgency_level` (Low/Medium/High), a one-sentence `chief_complaint`, and `suggested_questions`. This structured output directly maps to our frontend UI.
- **Post-visit:** The LLM transforms raw clinical notes into a patient-friendly summary, extracting a medication schedule and actionable follow-up steps.

**Failure Handling:**
Crucially, AI generation **never blocks the core booking flow**. 
- Pre-visit summaries are generated as a background task immediately after booking.
- Post-visit summaries are generated after the doctor clicks "Complete Consultation".
If the LLM provider experiences an outage, the task catches the exception, retries using exponential backoff, and eventually falls back to a gracefully degraded state (e.g., "AI Summary temporarily unavailable"). The primary appointment lifecycle remains entirely unaffected.

## 4. Database Schema & API Design
### Database Schema
The database uses PostgreSQL with SQLAlchemy 2.0 (async). The schema is highly normalized across 13 core tables, using UUID primary keys for security and distributed generation.
- **Role separation:** `User` handles authentication and RBAC, while `Patient` and `Doctor` tables hold domain-specific profile data (1:1 relationship with `User`).
- **Materialized Slots:** Unlike systems that compute slots on-the-fly, `AppointmentSlot` records are physically materialized in the database. This allows us to use standard foreign keys and row-level locks, vastly simplifying concurrency management.
- **Granular Medical Records:** `Consultation`, `Prescription`, and `Medication` are distinct tables to allow complex queries (e.g., "Find all active medications for patient X").

### API Design
The RESTful API is built with FastAPI. It follows a strictly layered, feature-based module pattern:
- **Routers** handle HTTP concerns (status codes, dependency injection).
- **Services** encapsulate all complex business logic, acting as the single source of truth for transactions.
- **Pydantic v2 schemas** rigorously validate all incoming data before it touches the business layer.
Every endpoint enforces Role-Based Access Control via a `require_role(["patient", "doctor", "admin"])` dependency.

## 5. Third-Party Integrations
- **Email:** Integrated via SMTP. Dynamic HTML templates are rendered with context injected from the database (e.g., appointment dates, doctor names).
- **Google Calendar:** Integrated using OAuth 2.0. Background tasks use the Google API to create events upon booking, update them upon rescheduling, and delete them upon cancellation, ensuring the patient's calendar always reflects their true state.
