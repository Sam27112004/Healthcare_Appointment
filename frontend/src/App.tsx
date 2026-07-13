import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ROUTES } from './config/routes'
import { ProtectedRoute } from './components/common/ProtectedRoute'
import { LoginPage } from './features/auth/pages/LoginPage'
import { RegisterPage } from './features/auth/pages/RegisterPage'
import { PatientDashboard } from './features/patient/pages/PatientDashboard'
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
          <Route path={ROUTES.PATIENT_DASHBOARD} element={<PatientDashboard />} />
        </Route>

        {/* Doctor Routes */}
        <Route element={<ProtectedRoute roles={['doctor']} />}>
          <Route path={ROUTES.DOCTOR_DASHBOARD} element={<DoctorDashboard />} />
        </Route>

        {/* Admin Routes */}
        <Route element={<ProtectedRoute roles={['admin']} />}>
          <Route path={ROUTES.ADMIN_DASHBOARD} element={<AdminDashboard />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to={ROUTES.LOGIN} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
