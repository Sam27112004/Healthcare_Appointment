export const ROUTES = {
  // Public
  LOGIN: '/login',
  REGISTER: '/register',

  // Patient
  PATIENT_DASHBOARD: '/patient/dashboard',
  DOCTOR_SEARCH: '/patient/doctors',
  DOCTOR_PROFILE: '/patient/doctors/:doctorId',
  SLOT_SELECTION: '/patient/doctors/:doctorId/slots',
  BOOKING_REVIEW: '/patient/booking/review',
  APPOINTMENTS: '/patient/appointments',
  APPOINTMENT_DETAILS: '/patient/appointments/:appointmentId',
  POST_VISIT_SUMMARY: '/patient/appointments/:appointmentId/summary',

  // Doctor
  DOCTOR_DASHBOARD: '/doctor/dashboard',

  // Admin
  ADMIN_DASHBOARD: '/admin/dashboard',
} as const;
