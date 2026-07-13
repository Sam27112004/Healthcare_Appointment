import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface AppLayoutProps {
  role: 'patient' | 'doctor' | 'admin';
}

export function AppLayout({ role }: AppLayoutProps) {
  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900">
      {/* Sidebar - fixed on desktop, hidden on mobile unless toggled */}
      <Sidebar role={role} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        {/* Scrollable page content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-50 dark:bg-slate-900 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
