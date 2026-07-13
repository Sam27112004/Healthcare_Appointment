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
      case 'scheduled': return <Badge variant="default" className="bg-blue-500">{formatStatus(status)}</Badge>;
      case 'completed': return <Badge variant="default" className="bg-green-500">{formatStatus(status)}</Badge>;
      case 'cancelled': return <Badge variant="destructive">{formatStatus(status)}</Badge>;
      default: return <Badge variant="outline">{formatStatus(status)}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Doctor Dashboard</h1>
        <p className="text-slate-500">Overview of your schedule for today.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Appointments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{appointments.length}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Today's Schedule</CardTitle>
          <CardDescription>{format(new Date(), 'MMMM d, yyyy')}</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-slate-500">Loading schedule...</div>
          ) : appointments.length === 0 ? (
            <div className="text-center py-12 text-slate-500 bg-slate-50 rounded-lg">
              You have no appointments scheduled for today.
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
