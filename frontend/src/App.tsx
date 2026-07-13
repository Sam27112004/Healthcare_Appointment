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

import { DoctorDashboard } from './features/doctor/pages/DoctorDashboard'
import { AdminDashboard } from './features/admin/pages/AdminDashboard'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />

        {/* Patient Routes */}
        <Route element={<ProtectedRoute roles={['patient']} />}>
          <Route element={<AppLayout role="patient" />}>
            <Route path={ROUTES.PATIENT_DASHBOARD} element={<PatientDashboard />} />
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
          </Route>
        </Route>

        {/* Admin Routes */}
        <Route element={<ProtectedRoute roles={['admin']} />}>
          <Route element={<AppLayout role="admin" />}>
            <Route path={ROUTES.ADMIN_DASHBOARD} element={<AdminDashboard />} />
          </Route>
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to={ROUTES.LOGIN} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
