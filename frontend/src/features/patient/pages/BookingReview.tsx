import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAppointmentStore } from '../../../stores/appointmentStore';
import { ROUTES } from '../../../config/routes';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Textarea } from '../../../components/ui/textarea';
import { Label } from '../../../components/ui/label';
import { Clock } from 'lucide-react';

const symptomSchema = z.object({
  symptoms: z.string().min(10, 'Please describe your symptoms in at least 10 characters'),
});

type SymptomFormData = z.infer<typeof symptomSchema>;

export function BookingReview() {
  const navigate = useNavigate();
  const { 
    selectedSlot, 
    heldSlotId, 
    holdExpiresAt, 
    setSymptoms, 
    confirmBooking, 
    resetBookingFlow,
    isLoading,
    error
  } = useAppointmentStore();

  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [bookingError, setBookingError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SymptomFormData>({
    resolver: zodResolver(symptomSchema),
  });

  useEffect(() => {
    if (!heldSlotId || !selectedSlot) {
      navigate(ROUTES.DOCTOR_SEARCH);
      return;
    }

    if (!holdExpiresAt) return;

    const interval = setInterval(() => {
      const remaining = Math.max(0, new Date(holdExpiresAt).getTime() - Date.now());
      setTimeLeft(Math.floor(remaining / 1000));
      
      if (remaining <= 0) {
        clearInterval(interval);
        resetBookingFlow();
        alert('Your slot hold has expired. Please select a slot again.');
        navigate(`/patient/doctors/${selectedSlot.doctor_id}/slots`);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [heldSlotId, selectedSlot, holdExpiresAt, navigate, resetBookingFlow]);

  const onSubmit = async (data: SymptomFormData) => {
    setBookingError(null);
    try {
      setSymptoms(data.symptoms);
      await confirmBooking();
      resetBookingFlow();
      navigate(ROUTES.PATIENT_DASHBOARD);
    } catch (err: any) {
      setBookingError(err.response?.data?.detail || 'Booking failed');
    }
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  if (!selectedSlot) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Review & Confirm</h1>
        <p className="text-slate-500">Provide your symptoms and confirm your appointment.</p>
      </div>

      <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-4 flex items-center dark:bg-blue-900/30 dark:border-blue-800 dark:text-blue-300">
        <Clock className="w-5 h-5 mr-3" />
        <div>
          <span className="font-semibold">Slot held for {formatTime(timeLeft)}</span>
          <p className="text-sm">Complete this form before the timer expires to secure your appointment.</p>
        </div>
      </div>

      <Card className="border-none shadow-sm">
        <CardHeader className="bg-slate-50 border-b">
          <CardTitle>Appointment Details</CardTitle>
          <CardDescription>Review the date and time</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-slate-500">Date</p>
              <p className="font-medium">{selectedSlot.slot_date}</p>
            </div>
            <div>
              <p className="text-slate-500">Time</p>
              <p className="font-medium">{selectedSlot.start_time.substring(0,5)} - {selectedSlot.end_time.substring(0,5)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-none shadow-sm">
        <CardHeader className="bg-slate-50 border-b">
          <CardTitle>Symptoms</CardTitle>
          <CardDescription>Tell the doctor why you are visiting</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="symptoms">Describe your symptoms</Label>
              <Textarea 
                id="symptoms" 
                placeholder="I have been experiencing a mild headache and fever since yesterday..." 
                rows={5}
                {...register('symptoms')}
                className={errors.symptoms ? 'border-red-500' : ''}
              />
              {errors.symptoms && (
                <p className="text-sm text-red-500">{errors.symptoms.message}</p>
              )}
            </div>

            {(bookingError || error) && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md dark:bg-red-900/50 dark:text-red-200">
                {bookingError || error}
              </div>
            )}

            <div className="flex gap-4 pt-4">
              <Button 
                type="button" 
                variant="outline" 
                className="w-full"
                onClick={() => {
                  resetBookingFlow();
                  navigate(-1);
                }}
              >
                Cancel
              </Button>
              <Button type="submit" className="w-full" disabled={isLoading || timeLeft <= 0}>
                {isLoading ? 'Confirming...' : 'Confirm Booking'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
