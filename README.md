# Healthcare Appointment & Follow-up Manager

> A production-inspired healthcare appointment platform that manages the complete patient appointment lifecycle — from intelligent scheduling and AI-assisted communication to automated reminders and Google Calendar integration.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Database Setup](#database-setup)
  - [Redis & Celery Setup](#redis--celery-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [LLM Prompts](#llm-prompts)
- [Google Calendar Setup](#google-calendar-setup)
- [Email Configuration](#email-configuration)
- [Deployment](#deployment)
- [Testing](#testing)
- [Project Documentation](#project-documentation)
- [License](#license)

---

## Overview

This platform transforms appointment booking into a complete healthcare coordination workflow. It combines:

- **Intelligent Scheduling** — Recurring weekly schedules with leave overrides, slot hold mechanisms, and concurrency-safe booking.
- **AI-Assisted Communication** — Gemini-powered pre-visit summaries for doctors and patient-friendly post-visit summaries.
- **Automated Reminders** — Medication reminders based on prescription frequency, appointment reminders, and email notifications.
- **Google Calendar Integration** — Automatic calendar event creation, update, and deletion for both patients and doctors.
- **Role-Based Access Control** — Separate portals and dashboards for Patients, Doctors, and Clinic Administrators.

### Target Users

| Role | Description |
|------|-------------|
| **Patient** | Registers, searches doctors, books appointments, fills symptom forms, views summaries and prescriptions |
| **Doctor** | Views AI pre-visit summaries, writes consultation notes, creates prescriptions, completes consultations |
| **Admin** | Manages doctors, specializations, configures schedules, marks leave, monitors appointments |

---

## Key Features

### Patient Portal
- Register / Login / Logout
- Search doctors by specialization
- View doctor profiles and available slots
- Book, cancel, and reschedule appointments
- Fill symptoms before confirmation
- View upcoming & past appointments
- View patient-friendly post-visit summary
- View prescriptions
- Receive booking / reminder / cancellation emails
- Receive medication reminders
- Receive Google Calendar invites

### Doctor Portal
- View dashboard with today's appointments
- View AI-generated pre-visit summary (urgency level, chief complaint, suggested questions)
- Write consultation notes
- Create prescriptions (multiple medicines per prescription)
- Complete consultations

### Admin Portal
- Manage doctor profiles
- Manage specializations
- Configure recurring weekly schedules
- Mark doctor leave (with automatic patient notification for affected bookings)
- Monitor all appointments

### System Guardrails
- Prevent doctor double-booking
- Prevent overlapping appointments for the same patient
- Prevent booking unavailable / leave slots
- Prevent booking outside working hours
- Role-based access control (RBAC)
- Appointment booking succeeds even if AI fails
- Slot hold mechanism prevents race conditions during concurrent booking

---

## Architecture at a Glance

```
┌─────────────────┐       HTTPS        ┌──────────────────────────┐
│   React + Vite  │ ──── Axios ──────► │        FastAPI           │
│   (TypeScript)  │                    │   ┌──────────────────┐   │
│                 │ ◄── JSON ────────  │   │ Auth Module      │   │
│  Tailwind CSS   │                    │   │ Patient Module   │   │
│  shadcn/ui      │                    │   │ Doctor Module    │   │
│  Zustand        │                    │   │ Admin Module     │   │
│  React Router   │                    │   │ Appointment Mod  │   │
└─────────────────┘                    │   │ AI Module        │   │
                                       │   │ Notification Mod │   │
                                       │   │ Calendar Module  │   │
                                       │   └──────────────────┘   │
                                       │          │               │
                                       │    SQLAlchemy 2.0        │
                                       │    Pydantic v2           │
                                       └──────────┬───────────────┘
                                                  │
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                         ┌────▼─────┐       ┌─────▼──────┐     ┌──────▼───────┐
                         │PostgreSQL│       │   Redis     │     │   Celery     │
                         │ (Neon)   │       │  (Upstash)  │     │  Workers     │
                         └──────────┘       └────────────┘     └──────┬───────┘
                                                                      │
                                                        ┌─────────────┼─────────────┐
                                                        │             │             │
                                                   ┌────▼───┐  ┌─────▼────┐  ┌─────▼─────┐
                                                   │ Gemini │  │  Email   │  │  Google   │
                                                   │  API   │  │ Service  │  │ Calendar  │
                                                   └────────┘  └──────────┘  └───────────┘
```

---

## Technology Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 18+ | UI library |
| Vite | Build tool & dev server |
| TypeScript | Type safety |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Component library |
| React Router v6 | Client-side routing |
| Axios | HTTP client |
| React Hook Form | Form management |
| Zod | Schema validation |
| Zustand | State management |

### Backend
| Technology | Purpose |
|-----------|---------|
| FastAPI | Web framework |
| SQLAlchemy 2.0 | ORM (async support) |
| Alembic | Database migrations |
| Pydantic v2 | Data validation & serialization |
| Passlib (bcrypt) | Password hashing |
| python-jose | JWT token handling |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| PostgreSQL | Primary database |
| Redis | Message broker & caching |
| Celery | Distributed task queue |

### AI
| Technology | Purpose |
|-----------|---------|
| Gemini 2.5 Flash / Flash-Lite | LLM provider via AI Service abstraction |

### Integrations
| Technology | Purpose |
|-----------|---------|
| FastAPI-Mail / SMTP | Email notifications |
| Google Calendar API | Calendar event management (OAuth 2.0) |

### Deployment
| Platform | Component |
|----------|-----------|
| Vercel | Frontend hosting |
| Render / Railway | Backend hosting |
| Neon PostgreSQL | Managed database |
| Upstash | Managed Redis |

---

## Prerequisites

- **Python** 3.11+
- **uv** (Python package manager — install from https://docs.astral.sh/uv/)
- **Node.js** 18+ and npm 9+
- **PostgreSQL** 15+
- **Redis** 7+
- **Git**

---

## Project Setup

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/healthcare-appointment-manager.git
cd healthcare-appointment-manager

# Set up backend with uv
cd backend
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
uv run alembic upgrade head

# Seed the database
uv run python scripts/seed_db.py

# Start the backend server
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env with your API URL

# Start the development server
npm run dev
```

### Database Setup

```bash
# Create the PostgreSQL database
createdb healthcare_db

# Or using psql
psql -U postgres -c "CREATE DATABASE healthcare_db;"

# Run migrations
cd backend
alembic upgrade head
```

### Redis & Celery Setup

```bash
# Start Redis server (local development)
redis-server

# Start Celery worker (from backend directory)
celery -A app.celery_app worker --loglevel=info

# Start Celery Beat (for periodic tasks like medication reminders)
celery -A app.celery_app beat --loglevel=info
```

---

## Environment Variables

See `.env.example` for the complete list. Key variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/healthcare_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI / Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Email
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@healthcare-app.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Google Calendar
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/calendar/callback

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## API Documentation

Once the backend is running, access the interactive API docs at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Database Schema

The system uses 13 core tables.

---

## LLM Prompts

### Pre-Visit Summary Prompt
```
Analyse these symptoms and return a JSON object with:
- urgency_level: "Low" | "Medium" | "High"
- chief_complaint: string (one-sentence summary)
- suggested_questions: string[] (three questions the doctor should ask)

Patient symptoms: {symptoms}
```

### Post-Visit Summary Prompt
```
Convert these clinical notes into a patient-friendly summary as a JSON object with:
- summary: string (plain-language explanation of diagnosis and treatment)
- medication_schedule: object[] (each with name, dosage, frequency, duration, instructions)
- follow_up_steps: string[] (actionable next steps for the patient)

Clinical notes: {notes}
Prescription: {prescription_details}
```

> **Failure Handling**: AI generation runs asynchronously via Celery. If the LLM call fails, the system retries with exponential backoff (max 3 retries). The appointment booking always succeeds regardless of AI status. A fallback message is stored if all retries fail.

---

## Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Calendar API**
4. Create **OAuth 2.0 Client ID** credentials (Web application type)
5. Add authorized redirect URI: `http://localhost:8000/api/v1/calendar/callback`
6. Download the credentials JSON and set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
7. On first use, the system will prompt for OAuth consent to access the user's calendar

For production, update the redirect URI to your deployed backend URL.

---

## Email Configuration

The system uses SMTP for email delivery. For development, you can use Gmail with an App Password:

1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Set `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env`

For production, use a transactional email service (SendGrid, Mailgun, etc.).

---

## Deployment

| Component | Platform | Guide |
|-----------|----------|-------|
| Frontend | Vercel | Connect GitHub repo, set `VITE_API_BASE_URL` |
| Backend | Render / Railway | Docker deployment with `Dockerfile` |
| Database | Neon PostgreSQL | Create database, copy connection string |
| Redis | Upstash | Create Redis instance, copy connection URL |

---

## Testing

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```


## License

This project is developed as an academic assignment. All rights reserved.
