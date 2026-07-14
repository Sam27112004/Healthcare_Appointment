export const ROUTES = {
  // Public
  LOGIN: '/login',
  REGISTER: '/register',

  // Patient
  PATIENT_DASHBOARD: '/patient/dashboard',
  PATIENT_PROFILE: '/patient/profile',
  DOCTOR_SEARCH: '/patient/doctors',
  DOCTOR_PROFILE: '/patient/doctors/:doctorId',
  SLOT_SELECTION: '/patient/doctors/:doctorId/slots',
  BOOKING_REVIEW: '/patient/booking/review',
  APPOINTMENTS: '/patient/appointments',
  APPOINTMENT_DETAILS: '/patient/appointments/:appointmentId',
  POST_VISIT_SUMMARY: '/patient/appointments/:appointmentId/summary',

  // Doctor
  DOCTOR_DASHBOARD: '/doctor/dashboard',
  DOCTOR_APPOINTMENTS: '/doctor/appointments',
  DOCTOR_APPOINTMENT_DETAILS: '/doctor/appointments/:appointmentId',
  DOCTOR_CONSULTATION: '/doctor/appointments/:appointmentId/consultation',

  // Admin
  ADMIN_DASHBOARD: '/admin/dashboard',
  ADMIN_DOCTORS: '/admin/doctors',
  ADMIN_SPECIALIZATIONS: '/admin/specializations',
  ADMIN_APPOINTMENTS: '/admin/appointments',
  ADMIN_DOCTOR_SCHEDULE: '/admin/doctors/:doctorId/schedule',
  ADMIN_DOCTOR_LEAVES: '/admin/doctors/:doctorId/leaves',
  ADMIN_SETTINGS: '/admin/settings',
} as const;
