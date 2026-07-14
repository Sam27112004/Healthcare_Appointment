import { useState, useEffect } from 'react';
import { adminApi } from '../services/adminApi';
import { Card } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { toast } from '../../../hooks/use-toast';
import { Calendar, Clock, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

export function AppointmentMonitor() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const limit = 15;

  useEffect(() => {
    fetchAppointments();
  }, [page, statusFilter]);

  const fetchAppointments = async () => {
    setIsLoading(true);
    try {
      const params: any = { page, limit };
      if (statusFilter !== 'all') params.status = statusFilter;
      
      const data = await adminApi.getAllAppointments(params);
      setAppointments(data.items || []);
      setTotalPages(data.pages || 1);
    } catch (e) {
      toast({ variant: 'destructive', title: 'Error', description: 'Failed to load appointments' });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'booked': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'cancelled': return 'bg-red-100 text-red-800 border-red-200';
      case 'no_show': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  return (
    <div className="space-y-8 animate-fade-in-up">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-heading font-extrabold tracking-tight text-gradient">Appointment Monitor</h1>
          <p className="text-slate-500 mt-1">Monitor all appointments across the platform in real-time.</p>
        </div>
        
        <div className="flex items-center space-x-2 bg-white/50 dark:bg-slate-900/50 p-1.5 rounded-lg border border-slate-200/60 dark:border-slate-800/60 backdrop-blur-sm">
          <span className="text-sm text-slate-500 font-medium px-2">Status:</span>
          <Select value={statusFilter} onValueChange={(val) => { setStatusFilter(val); setPage(1); }}>
            <SelectTrigger className="w-[160px] bg-white dark:bg-slate-900 border-none shadow-sm focus:ring-1 focus:ring-primary/20">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="booked">Booked</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
              <SelectItem value="no_show">No Show</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50/50 border-b">
              <tr>
                <th className="px-6 py-4 font-semibold">Patient</th>
                <th className="px-6 py-4 font-semibold">Doctor</th>
                <th className="px-6 py-4 font-semibold">Date & Time</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Booked At</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading appointments...
                  </td>
                </tr>
              ) : appointments.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    <Calendar className="w-12 h-12 mx-auto mb-2 text-slate-300" />
                    No appointments found matching your criteria.
                  </td>
                </tr>
              ) : (
                appointments.map((apt) => (
                  <tr key={apt.id} className="border-b hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-semibold mr-3">
                          {apt.patient?.user?.full_name?.charAt(0) || 'P'}
                        </div>
                        <div>
                          <div className="font-medium text-slate-900">{apt.patient?.user?.full_name}</div>
                          <div className="text-xs text-slate-500">{apt.patient?.user?.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-900">Dr. {apt.doctor?.user?.full_name}</div>
                      <div className="text-xs text-slate-500">{apt.doctor?.specialization?.name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-900 flex items-center">
                        <Calendar className="w-3 h-3 mr-1 text-slate-400" />
                        {apt.slot?.slot_date}
                      </div>
                      <div className="text-xs text-slate-500 flex items-center mt-1">
                        <Clock className="w-3 h-3 mr-1 text-slate-400" />
                        {apt.slot?.start_time?.substring(0, 5)} - {apt.slot?.end_time?.substring(0, 5)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="outline" className={`capitalize ${getStatusColor(apt.status)}`}>
                        {apt.status.replace('_', ' ')}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs">
                      {new Date(apt.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {!isLoading && totalPages > 1 && (
          <div className="px-6 py-4 border-t bg-slate-50/50 flex items-center justify-between">
            <span className="text-sm text-slate-500">
              Showing page {page} of {totalPages}
            </span>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
