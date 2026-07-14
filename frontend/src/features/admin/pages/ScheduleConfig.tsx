import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminApi } from '../services/adminApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Checkbox } from '../../../components/ui/checkbox';
import { ArrowLeft } from 'lucide-react';

const DAYS = [
  { id: 0, name: 'Monday' },
  { id: 1, name: 'Tuesday' },
  { id: 2, name: 'Wednesday' },
  { id: 3, name: 'Thursday' },
  { id: 4, name: 'Friday' },
  { id: 5, name: 'Saturday' },
  { id: 6, name: 'Sunday' },
];

export function ScheduleConfig() {
  const { doctorId } = useParams<{ doctorId: string }>();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Default state for all days
  const [schedule, setSchedule] = useState(
    DAYS.reduce((acc, day) => {
      acc[day.id] = { active: false, start_time: '09:00', end_time: '17:00' };
      return acc;
    }, {} as any)
  );

  useEffect(() => {
    if (!doctorId) return;
    const fetchSchedule = async () => {
      try {
        const existingSchedules = await adminApi.getSchedule(doctorId);
        if (existingSchedules && existingSchedules.length > 0) {
          setSchedule((prev: any) => {
            const newSchedule = { ...prev };
            existingSchedules.forEach((s: any) => {
              newSchedule[s.day_of_week] = {
                active: true,
                start_time: s.start_time.substring(0, 5), // e.g., "09:00:00" -> "09:00"
                end_time: s.end_time.substring(0, 5)
              };
            });
            return newSchedule;
          });
        }
      } catch (e) {
        console.error('Failed to fetch existing schedule', e);
      }
    };
    fetchSchedule();
  }, [doctorId]);

  const handleToggleDay = (dayId: number, checked: boolean) => {
    setSchedule((prev: any) => ({
      ...prev,
      [dayId]: { ...prev[dayId], active: checked }
    }));
  };

  const handleTimeChange = (dayId: number, field: string, value: string) => {
    setSchedule((prev: any) => ({
      ...prev,
      [dayId]: { ...prev[dayId], [field]: value }
    }));
  };

  const onSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Find all active days and submit them
      const promises = Object.keys(schedule).map(async (dayIdStr) => {
        const dayId = parseInt(dayIdStr);
        const config = schedule[dayId];
        if (config.active) {
          await adminApi.createSchedule(doctorId!, {
            day_of_week: dayId,
            start_time: config.start_time,
            end_time: config.end_time,
            slot_duration: 30
          });
        }
      });
      
      await Promise.all(promises);
      
      // Auto-generate slots for the next 30 days
      const today = new Date();
      const nextMonth = new Date();
      nextMonth.setDate(today.getDate() + 30);
      
      const startDate = today.toISOString().split('T')[0];
      const endDate = nextMonth.toISOString().split('T')[0];
      
      await adminApi.generateSlots(doctorId!, startDate, endDate);
      
      alert('Schedule configured and slots generated successfully!');
      navigate('/admin/doctors');
    } catch (e) {
      console.error(e);
      alert('Failed to configure schedule');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/admin/doctors')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Configure Schedule</h1>
          <p className="text-slate-500">Set weekly recurring availability.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Weekly Hours</CardTitle>
          <CardDescription>Select the days and times the doctor is available. Each slot is 30 minutes.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {DAYS.map((day) => {
            const config = schedule[day.id];
            return (
              <div key={day.id} className="flex items-center gap-6 p-4 rounded-lg border bg-slate-50">
                <div className="flex items-center space-x-2 w-32">
                  <Checkbox 
                    id={`day-${day.id}`} 
                    checked={config.active}
                    onCheckedChange={(c) => handleToggleDay(day.id, c as boolean)}
                  />
                  <Label htmlFor={`day-${day.id}`} className="font-medium cursor-pointer">{day.name}</Label>
                </div>
                
                <div className={`flex items-center gap-4 flex-1 ${!config.active && 'opacity-50 pointer-events-none'}`}>
                  <div className="space-y-1">
                    <Label className="text-xs text-slate-500">Start Time</Label>
                    <Input 
                      type="time" 
                      value={config.start_time}
                      onChange={(e) => handleTimeChange(day.id, 'start_time', e.target.value)}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs text-slate-500">End Time</Label>
                    <Input 
                      type="time" 
                      value={config.end_time}
                      onChange={(e) => handleTimeChange(day.id, 'end_time', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            );
          })}
          
          <div className="flex justify-end pt-4">
            <Button onClick={onSubmit} disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Schedule'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
