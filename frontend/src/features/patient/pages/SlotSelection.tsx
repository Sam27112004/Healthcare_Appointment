import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { patientApi } from '../services/patientApi';
import { appointmentApi } from '../services/appointmentApi';
import { useAppointmentStore } from '../../../stores/appointmentStore';
import { ROUTES } from '../../../config/routes';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Calendar } from '../../../components/ui/calendar';
import { format } from 'date-fns';

export function SlotSelection() {
  const { doctorId } = useParams<{ doctorId: string }>();
  const navigate = useNavigate();
  
  const [doctor, setDoctor] = useState<any>(null);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [slots, setSlots] = useState<any[]>([]);
  const [isLoadingSlots, setIsLoadingSlots] = useState(false);
  
  const { holdSlot, isLoading: isHolding, error: holdError } = useAppointmentStore();

  useEffect(() => {
    if (doctorId) fetchDoctor(doctorId);
  }, [doctorId]);

  useEffect(() => {
    if (doctorId && selectedDate) {
      fetchSlots(doctorId, format(selectedDate, 'yyyy-MM-dd'));
    }
  }, [doctorId, selectedDate]);

  const fetchDoctor = async (id: string) => {
    try {
      const data = await patientApi.getDoctor(id);
      setDoctor(data);
    } catch (e) {
      console.error("Failed to fetch doctor");
    }
  };

  const fetchSlots = async (id: string, dateStr: string) => {
    setIsLoadingSlots(true);
    try {
      const data = await appointmentApi.getAvailableSlots(id, dateStr);
      setSlots(data.slots || []);
    } catch (e) {
      console.error("Failed to fetch slots");
    } finally {
      setIsLoadingSlots(false);
    }
  };

  const handleSlotClick = async (slot: any) => {
    try {
      await holdSlot(slot);
      navigate(ROUTES.BOOKING_REVIEW);
    } catch (e) {
      // Error is handled in store and displayed in UI
    }
  };

  if (!doctor) return <div className="p-8 text-center">Loading doctor profile...</div>;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Select a Time Slot</h1>
        <p className="text-slate-500">Choose an available time to consult with Dr. {doctor.user?.full_name}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Doctor Info */}
        <Card className="md:col-span-1 border-none shadow-sm h-fit">
          <CardHeader className="bg-slate-50 border-b pb-4">
            <CardTitle className="text-xl">Dr. {doctor.user?.full_name}</CardTitle>
            <CardDescription>
              <Badge variant="secondary" className="mt-1">
                {doctor.specialization?.name}
              </Badge>
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
             <div>
              <p className="text-sm font-medium text-slate-500">Qualifications</p>
              <p className="text-sm">{doctor.qualifications}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Experience</p>
              <p className="text-sm">{doctor.experience_years} years</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Consultation Fee</p>
              <p className="text-lg font-semibold">${doctor.consultation_fee}</p>
            </div>
          </CardContent>
        </Card>

        {/* Date & Slot Picker */}
        <div className="md:col-span-2 space-y-6">
          <Card className="border-none shadow-sm">
            <CardContent className="p-6 flex flex-col md:flex-row gap-8">
              <div>
                <h3 className="font-medium mb-4">Select Date</h3>
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  className="rounded-md border shadow"
                  disabled={(date) => date < new Date(new Date().setHours(0,0,0,0))}
                />
              </div>
              
              <div className="flex-1">
                <h3 className="font-medium mb-4">Available Slots</h3>
                
                {holdError && (
                  <div className="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
                    {holdError}
                  </div>
                )}

                {isLoadingSlots ? (
                  <div className="text-sm text-slate-500">Loading slots...</div>
                ) : slots.length === 0 ? (
                  <div className="text-sm text-slate-500 bg-slate-50 p-4 rounded-md border border-dashed border-slate-200">
                    No available slots on this date.
                  </div>
                ) : (
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                    {slots.map((slot) => (
                      <Button
                        key={slot.id}
                        variant={slot.status === 'available' ? 'outline' : 'secondary'}
                        className={`w-full ${slot.status !== 'available' ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-500 hover:text-blue-600'}`}
                        disabled={slot.status !== 'available' || isHolding}
                        onClick={() => handleSlotClick(slot)}
                      >
                        {slot.start_time.substring(0,5)}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
