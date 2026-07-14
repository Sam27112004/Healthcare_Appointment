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
          { name: 'Profile', href: ROUTES.PATIENT_PROFILE, icon: Settings },
        ];
      case 'doctor':
        return [
          { name: 'Dashboard', href: ROUTES.DOCTOR_DASHBOARD, icon: Home },
          { name: 'My Schedule', href: '/doctor/appointments', icon: Calendar },
        ];
      case 'admin':
        return [
          { name: 'Dashboard', href: ROUTES.ADMIN_DASHBOARD, icon: Activity },
          { name: 'Appointments', href: ROUTES.ADMIN_APPOINTMENTS, icon: Calendar },
          { name: 'Doctors', href: '/admin/doctors', icon: Users },
          { name: 'Specializations', href: ROUTES.ADMIN_SPECIALIZATIONS, icon: Activity },
          { name: 'Settings', href: '/admin/settings', icon: Settings },
        ];
      default:
        return [];
    }
  };

  const links = getLinks();

  return (
    <aside className="w-64 glass-panel border-r-0 flex flex-col hidden md:flex shadow-xl z-50">
      <div className="h-16 flex items-center px-6 border-b border-slate-200/50 dark:border-slate-800/50 bg-white/40 dark:bg-slate-900/40">
        <div className="bg-gradient-to-tr from-primary to-indigo-500 p-2 rounded-lg mr-3 shadow-glow">
          <Activity className="h-5 w-5 text-white" />
        </div>
        <span className="font-heading font-bold text-xl tracking-tight text-slate-900 dark:text-white">HealthManager</span>
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
                  'group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-300 relative overflow-hidden',
                  isActive
                    ? 'text-primary dark:text-blue-300 bg-primary/10 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-200 hover:translate-x-1'
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-r-md shadow-glow" />
                  )}
                  <Icon className={cn(
                    "mr-3 h-5 w-5 flex-shrink-0 transition-transform duration-300",
                    isActive ? "text-primary scale-110" : "text-slate-400 group-hover:text-primary/70"
                  )} />
                  <span className="relative z-10">{link.name}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
