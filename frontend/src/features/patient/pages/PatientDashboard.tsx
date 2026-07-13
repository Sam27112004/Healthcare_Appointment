import { useState, useEffect } from 'react';
import { appointmentApi } from '../services/appointmentApi';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../../config/routes';

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
      case 'scheduled': return <Badge variant="default" className="bg-blue-500 text-white">{formatStatus(status)}</Badge>;
      case 'completed': return <Badge variant="default" className="bg-green-500 text-white">{formatStatus(status)}</Badge>;
      case 'cancelled': return <Badge variant="destructive">{formatStatus(status)}</Badge>;
      case 'no_show': return <Badge variant="secondary">{formatStatus(status)}</Badge>;
      default: return <Badge variant="outline">{formatStatus(status)}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Patient Dashboard</h1>
          <p className="text-slate-500">Manage your upcoming and past appointments.</p>
        </div>
        <Button onClick={() => navigate(ROUTES.DOCTOR_SEARCH)}>Book Appointment</Button>
      </div>

      <Card className="border-none shadow-sm">
        <CardHeader className="bg-slate-50 border-b">
          <CardTitle>My Appointments</CardTitle>
          <CardDescription>View all your health consultations</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="text-center py-8 text-slate-500">Loading appointments...</div>
          ) : appointments.length === 0 ? (
            <div className="text-center py-12 text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
              <p>You have no appointments yet.</p>
              <Button variant="outline" className="mt-4" onClick={() => navigate(ROUTES.DOCTOR_SEARCH)}>
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
