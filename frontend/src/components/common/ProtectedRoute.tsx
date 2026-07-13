import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { ROUTES } from '../../config/routes';

interface ProtectedRouteProps {
  roles: string[];
}

export function ProtectedRoute({ roles }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  if (!user || !roles.includes(user.role)) {
    // Redirect to appropriate dashboard
    const role = user?.role;
    if (role === 'admin') return <Navigate to={ROUTES.ADMIN_DASHBOARD} replace />;
    if (role === 'doctor') return <Navigate to={ROUTES.DOCTOR_DASHBOARD} replace />;
    if (role === 'patient') return <Navigate to={ROUTES.PATIENT_DASHBOARD} replace />;
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  return <Outlet />;
}
