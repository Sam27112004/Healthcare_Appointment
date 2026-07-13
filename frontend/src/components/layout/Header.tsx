import { useAuthStore } from '../../stores/authStore';
import { Button } from '../ui/button';
import { LogOut, User as UserIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../config/routes';

export function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 z-10">
      <div className="flex-1 flex md:hidden">
        {/* Mobile menu button could go here */}
      </div>

      <div className="ml-auto flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-sm text-slate-700 dark:text-slate-300">
          <UserIcon className="h-4 w-4" />
          <span className="font-medium">{user?.full_name}</span>
          <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-semibold uppercase tracking-wider dark:bg-slate-800 dark:text-slate-400">
            {user?.role}
          </span>
        </div>
        <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400">
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>
      </div>
    </header>
  );
}
