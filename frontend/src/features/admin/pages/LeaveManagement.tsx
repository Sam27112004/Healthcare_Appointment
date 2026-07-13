import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminApi } from '../services/adminApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { ArrowLeft } from 'lucide-react';

export function LeaveManagement() {
  const { doctorId } = useParams<{ doctorId: string }>();
  const navigate = useNavigate();
  const [date, setDate] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await adminApi.createLeave(doctorId!, date, reason);
      alert('Leave registered successfully. All appointments on this date have been cancelled.');
      navigate('/admin/doctors');
    } catch (error) {
      console.error(error);
      alert('Failed to register leave');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/admin/doctors')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Register Leave</h1>
          <p className="text-slate-500">Block off dates when the doctor is unavailable.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Leave Details</CardTitle>
          <CardDescription>
            Registering a leave will automatically cancel any existing appointments on that date.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input 
                id="date" 
                type="date" 
                required 
                value={date} 
                onChange={(e) => setDate(e.target.value)} 
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reason">Reason (Optional)</Label>
              <Input 
                id="reason" 
                value={reason} 
                onChange={(e) => setReason(e.target.value)} 
                placeholder="e.g. Personal vacation" 
              />
            </div>
            <div className="pt-4">
              <Button type="submit" variant="destructive" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? 'Registering...' : 'Register Leave & Cancel Appointments'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
