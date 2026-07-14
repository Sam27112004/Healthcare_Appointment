import { useState, useEffect } from 'react';
import { doctorApi } from '../services/doctorApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { formatTime, formatStatus } from '../../../lib/formatters';

export function DoctorDashboard() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTodayAppointments();
  }, []);

  const fetchTodayAppointments = async () => {
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      const data = await doctorApi.getAppointments({ date: today });
      setAppointments(data.items || data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'scheduled': return <Badge variant="default" className="bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 shadow-sm">{formatStatus(status)}</Badge>;
      case 'completed': return <Badge variant="default" className="bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 hover:bg-emerald-500/20 shadow-sm">{formatStatus(status)}</Badge>;
      case 'cancelled': return <Badge variant="destructive" className="bg-red-500/10 text-red-600 border border-red-500/20 hover:bg-red-500/20 shadow-sm">{formatStatus(status)}</Badge>;
      default: return <Badge variant="outline" className="shadow-sm">{formatStatus(status)}</Badge>;
    }
  };

  return (
    <div className="space-y-8 animate-fade-in-up">
      <div>
        <h1 className="text-3xl font-heading font-extrabold tracking-tight text-slate-900 dark:text-white">Doctor Dashboard</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Overview of your schedule and practice for today.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="glass-card bg-gradient-to-br from-primary/5 to-indigo-500/5">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600 dark:text-slate-300">Today's Appointments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-extrabold text-primary">{appointments.length}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card">
        <CardHeader className="bg-slate-50/50 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-800 rounded-t-xl">
          <CardTitle className="text-xl">Today's Schedule</CardTitle>
          <CardDescription>{format(new Date(), 'MMMM d, yyyy')}</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="text-center py-12 text-slate-500 animate-pulse-slow">
              <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin mx-auto mb-4" />
              Loading schedule...
            </div>
          ) : appointments.length === 0 ? (
            <div className="text-center py-16 text-slate-500 bg-slate-50/50 dark:bg-slate-900/20 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">Schedule Clear</h3>
              <p>You have no appointments scheduled for today.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Patient</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {appointments.map((appt) => (
                  <TableRow key={appt.id}>
                    <TableCell className="font-medium">
                      {formatTime(appt.slot?.start_time)}
                    </TableCell>
                    <TableCell>{appt.patient?.user?.full_name}</TableCell>
                    <TableCell>{getStatusBadge(appt.status)}</TableCell>
                    <TableCell className="text-right">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => navigate(`/doctor/appointments/${appt.id}`)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
