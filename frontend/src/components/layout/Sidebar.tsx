import { NavLink } from 'react-router-dom';
import { ROUTES } from '../../config/routes';
import { Home, Users, Calendar, Settings, Activity } from 'lucide-react';
import { cn } from '../../lib/utils';

interface SidebarProps {
  role: 'patient' | 'doctor' | 'admin';
}

export function Sidebar({ role }: SidebarProps) {
  const getLinks = () => {
    switch (role) {
      case 'patient':
        return [
          { name: 'Dashboard', href: ROUTES.PATIENT_DASHBOARD, icon: Home },
          { name: 'Find Doctor', href: ROUTES.DOCTOR_SEARCH, icon: Users },
          { name: 'Appointments', href: '/patient/appointments', icon: Calendar },
        ];
      case 'doctor':
        return [
          { name: 'Dashboard', href: ROUTES.DOCTOR_DASHBOARD, icon: Home },
          { name: 'My Schedule', href: '/doctor/appointments', icon: Calendar },
        ];
      case 'admin':
        return [
          { name: 'Dashboard', href: ROUTES.ADMIN_DASHBOARD, icon: Activity },
          { name: 'Doctors', href: '/admin/doctors', icon: Users },
          { name: 'Settings', href: '/admin/settings', icon: Settings },
        ];
      default:
        return [];
    }
  };

  const links = getLinks();

  return (
    <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
        <Activity className="h-6 w-6 text-blue-600 mr-2" />
        <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">HealthManager</span>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.name}
              to={link.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-200'
                    : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                )
              }
            >
              <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
              {link.name}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
