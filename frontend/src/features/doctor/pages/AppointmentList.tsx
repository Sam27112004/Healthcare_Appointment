import { useState, useEffect } from 'react';
import { doctorApi } from '../services/doctorApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { useNavigate } from 'react-router-dom';
import { formatDate, formatTime, formatStatus } from '../../../lib/formatters';

export function AppointmentList() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAppointments();
  }, [statusFilter]);

  const fetchAppointments = async () => {
    setIsLoading(true);
    try {
      const data = await doctorApi.getAppointments({ 
        status: statusFilter === 'all' ? undefined : statusFilter 
      });
      setAppointments(data.items || data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'booked': return <Badge variant="default" className="bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 shadow-sm">{formatStatus(status)}</Badge>;
      case 'completed': return <Badge variant="default" className="bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 hover:bg-emerald-500/20 shadow-sm">{formatStatus(status)}</Badge>;
      case 'cancelled': return <Badge variant="destructive" className="bg-red-500/10 text-red-600 border border-red-500/20 hover:bg-red-500/20 shadow-sm">{formatStatus(status)}</Badge>;
      case 'no_show': return <Badge variant="secondary" className="bg-slate-500/10 text-slate-600 border border-slate-500/20 hover:bg-slate-500/20 shadow-sm">{formatStatus(status)}</Badge>;
      default: return <Badge variant="outline" className="shadow-sm">{formatStatus(status)}</Badge>;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-heading font-extrabold tracking-tight text-slate-900 dark:text-white">My Schedule</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Manage all your appointments.</p>
        </div>
        <div className="w-48">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Appointments</SelectItem>
              <SelectItem value="scheduled">Scheduled</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card className="glass-card">
        <CardHeader className="bg-slate-50/50 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-800 rounded-t-xl">
          <CardTitle className="text-xl">Appointments</CardTitle>
          <CardDescription>A list of your consultations.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-slate-500">Loading schedule...</div>
          ) : appointments.length === 0 ? (
            <div className="text-center py-12 text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
              No appointments found for this filter.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Patient</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {appointments.map((appt) => (
                  <TableRow key={appt.id}>
                    <TableCell>{formatDate(appt.slot?.slot_date)}</TableCell>
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
