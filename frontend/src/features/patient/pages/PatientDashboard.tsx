import { useState, useEffect } from 'react';
import { appointmentApi } from '../services/appointmentApi';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../../config/routes';
import { Calendar } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { formatDate, formatTime, formatStatus } from '../../../lib/formatters';

export function PatientDashboard() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const data = await appointmentApi.getAppointments();
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
      case 'no_show': return <Badge variant="secondary" className="bg-slate-500/10 text-slate-600 border border-slate-500/20 hover:bg-slate-500/20 shadow-sm">{formatStatus(status)}</Badge>;
      default: return <Badge variant="outline" className="shadow-sm">{formatStatus(status)}</Badge>;
    }
  };

  return (
    <div className="space-y-8 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-heading font-extrabold tracking-tight text-slate-900 dark:text-white">Patient Dashboard</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Manage your upcoming and past appointments seamlessly.</p>
        </div>
        <Button 
          onClick={() => navigate(ROUTES.DOCTOR_SEARCH)}
          className="bg-primary hover:bg-primary/90 text-white shadow-md hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5 rounded-full px-6"
        >
          Book Appointment
        </Button>
      </div>

      <Card className="glass-card">
        <CardHeader className="bg-slate-50/50 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-800 rounded-t-xl">
          <CardTitle className="text-xl">My Appointments</CardTitle>
          <CardDescription>View and manage all your health consultations</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="text-center py-12 text-slate-500 animate-pulse-slow">
              <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin mx-auto mb-4" />
              Loading appointments...
            </div>
          ) : appointments.length === 0 ? (
            <div className="text-center py-16 text-slate-500 bg-slate-50/50 dark:bg-slate-900/20 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
              <div className="bg-white dark:bg-slate-800 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <Calendar className="h-8 w-8 text-primary/50" />
              </div>
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No Appointments Yet</h3>
              <p className="max-w-sm mx-auto text-sm text-slate-500 dark:text-slate-400 mb-6">You haven't booked any appointments. Start your healthcare journey today.</p>
              <Button onClick={() => navigate(ROUTES.DOCTOR_SEARCH)} className="rounded-full shadow-md">
                Find a Doctor
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Doctor</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {appointments.map((appt) => (
                  <TableRow key={appt.id}>
                    <TableCell className="font-medium">{formatDate(appt.slot?.slot_date)}</TableCell>
                    <TableCell>{formatTime(appt.slot?.start_time)}</TableCell>
                    <TableCell>Dr. {appt.doctor?.user?.full_name}</TableCell>
                    <TableCell>{getStatusBadge(appt.status)}</TableCell>
                    <TableCell className="text-right">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => navigate(`/patient/appointments/${appt.id}`)}
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
