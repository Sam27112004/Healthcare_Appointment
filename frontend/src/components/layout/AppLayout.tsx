import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface AppLayoutProps {
  role: 'patient' | 'doctor' | 'admin';
}

export function AppLayout({ role }: AppLayoutProps) {
  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-50/50 via-slate-50 to-slate-50 dark:from-blue-950/20 dark:via-slate-900 dark:to-slate-900">
      {/* Sidebar - fixed on desktop, hidden on mobile unless toggled */}
      <Sidebar role={role} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        {/* Scrollable page content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6 bg-transparent relative">
          <div className="absolute inset-0 bg-grid-slate-100/[0.04] bg-[bottom_1px_center] dark:bg-grid-slate-800/[0.04] pointer-events-none" style={{ maskImage: 'linear-gradient(to bottom, transparent, black)' }}></div>
          <div className="relative z-10 h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
