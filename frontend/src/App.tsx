import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ROUTES } from './config/routes'
import { ProtectedRoute } from './components/common/ProtectedRoute'
import { AppLayout } from './components/layout/AppLayout'

import { LoginPage } from './features/auth/pages/LoginPage'
import { RegisterPage } from './features/auth/pages/RegisterPage'

import { PatientDashboard } from './features/patient/pages/PatientDashboard'
import { DoctorSearch } from './features/patient/pages/DoctorSearch'
import { SlotSelection } from './features/patient/pages/SlotSelection'
import { BookingReview } from './features/patient/pages/BookingReview'
import { AppointmentDetails } from './features/patient/pages/AppointmentDetails'
import { PatientProfile } from './features/patient/pages/PatientProfile'

import { DoctorDashboard } from './features/doctor/pages/DoctorDashboard'
import { AdminDashboard } from './features/admin/pages/AdminDashboard'

import { AppointmentList } from './features/doctor/pages/AppointmentList'
import { AppointmentView } from './features/doctor/pages/AppointmentView'
import { ConsultationForm } from './features/doctor/pages/ConsultationForm'

import { DoctorManagement } from './features/admin/pages/DoctorManagement'
import { ScheduleConfig } from './features/admin/pages/ScheduleConfig'
import { LeaveManagement } from './features/admin/pages/LeaveManagement'
import { SpecializationManagement } from './features/admin/pages/SpecializationManagement'
import { AppointmentMonitor } from './features/admin/pages/AppointmentMonitor'
import { Toaster } from './components/ui/toaster'

function App() {
  return (
    <BrowserRouter>
      <Toaster />
      <Routes>
        {/* Public Routes */}
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />

        {/* Patient Routes */}
        <Route element={<ProtectedRoute roles={['patient']} />}>
          <Route element={<AppLayout role="patient" />}>
            <Route path={ROUTES.PATIENT_DASHBOARD} element={<PatientDashboard />} />
            <Route path={ROUTES.PATIENT_PROFILE} element={<PatientProfile />} />
            <Route path={ROUTES.APPOINTMENTS} element={<PatientDashboard />} />
            <Route path={ROUTES.DOCTOR_SEARCH} element={<DoctorSearch />} />
            <Route path={ROUTES.SLOT_SELECTION} element={<SlotSelection />} />
            <Route path={ROUTES.BOOKING_REVIEW} element={<BookingReview />} />
            <Route path={ROUTES.APPOINTMENT_DETAILS} element={<AppointmentDetails />} />
          </Route>
        </Route>

        {/* Doctor Routes */}
        <Route element={<ProtectedRoute roles={['doctor']} />}>
          <Route element={<AppLayout role="doctor" />}>
            <Route path={ROUTES.DOCTOR_DASHBOARD} element={<DoctorDashboard />} />
            <Route path={ROUTES.DOCTOR_APPOINTMENTS} element={<AppointmentList />} />
            <Route path={ROUTES.DOCTOR_APPOINTMENT_DETAILS} element={<AppointmentView />} />
            <Route path={ROUTES.DOCTOR_CONSULTATION} element={<ConsultationForm />} />
          </Route>
        </Route>

        {/* Admin Routes */}
        <Route element={<ProtectedRoute roles={['admin']} />}>
          <Route element={<AppLayout role="admin" />}>
            <Route path={ROUTES.ADMIN_DASHBOARD} element={<AdminDashboard />} />
            <Route path={ROUTES.ADMIN_APPOINTMENTS} element={<AppointmentMonitor />} />
            <Route path={ROUTES.ADMIN_DOCTORS} element={<DoctorManagement />} />
            <Route path={ROUTES.ADMIN_SPECIALIZATIONS} element={<SpecializationManagement />} />
            <Route path={ROUTES.ADMIN_DOCTOR_SCHEDULE} element={<ScheduleConfig />} />
            <Route path={ROUTES.ADMIN_DOCTOR_LEAVES} element={<LeaveManagement />} />
          </Route>
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to={ROUTES.LOGIN} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
