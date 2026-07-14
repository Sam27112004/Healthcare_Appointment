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
    <header className="h-16 sticky top-0 glass-panel border-b-0 flex items-center justify-between px-6 z-40 transition-all">
      <div className="flex-1 flex md:hidden">
        {/* Mobile menu button could go here */}
      </div>

      <div className="ml-auto flex items-center space-x-4">
        <div className="flex items-center space-x-3 text-sm text-slate-700 dark:text-slate-300">
          <div className="bg-primary/10 p-1.5 rounded-full text-primary">
            <UserIcon className="h-4 w-4" />
          </div>
          <span className="font-semibold text-slate-900 dark:text-white tracking-tight">{user?.full_name}</span>
          <span className="px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-widest dark:bg-primary/20">
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
