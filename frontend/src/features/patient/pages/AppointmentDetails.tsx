import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { appointmentApi } from '../services/appointmentApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { ArrowLeft, FileText, Activity, XCircle, CalendarClock, Pill } from 'lucide-react';
import { ROUTES } from '../../../config/routes';
import { toast } from '../../../hooks/use-toast';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { Textarea } from '../../../components/ui/textarea';

export function AppointmentDetails() {
  const { appointmentId } = useParams<{ appointmentId: string }>();
  const navigate = useNavigate();
  const [appointment, setAppointment] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [isCancelling, setIsCancelling] = useState(false);

  useEffect(() => {
    if (appointmentId) {
      fetchAppointment();
    }
  }, [appointmentId]);

  // Polling logic for pre-visit summary
  useEffect(() => {
    if (!appointment) return;
    
    // If AI is processing, poll every 5 seconds
    if (appointment.ai_pre_visit_status === 'processing' || appointment.ai_pre_visit_status === 'pending') {
      const interval = setInterval(() => {
        fetchAppointment(false);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [appointment?.ai_pre_visit_status]);

  const fetchAppointment = async (showLoader = true) => {
    if (showLoader) setIsLoading(true);
    try {
      // getPreVisitSummary actually returns the full appointment
      const data = await appointmentApi.getPreVisitSummary(appointmentId!);
      setAppointment(data);
    } catch (e) {
      console.error(e);
    } finally {
      if (showLoader) setIsLoading(false);
    }
  };

  const handleCancel = async () => {
    setIsCancelling(true);
    try {
      await appointmentApi.cancelAppointment(appointmentId!, cancelReason);
      toast({ title: 'Appointment Cancelled', description: 'Your appointment has been cancelled successfully.' });
      setIsCancelModalOpen(false);
      fetchAppointment(); // Refresh
    } catch (err: any) {
      toast({ variant: 'destructive', title: 'Error', description: err.response?.data?.detail || 'Failed to cancel appointment' });
    } finally {
      setIsCancelling(false);
    }
  };

  if (isLoading) return <div className="p-8 text-center">Loading details...</div>;
  if (!appointment) return <div className="p-8 text-center text-red-500">Appointment not found</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(ROUTES.PATIENT_DASHBOARD)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Appointment Details</h1>
            <p className="text-slate-500">Dr. {appointment.doctor?.user?.full_name} • {appointment.slot?.slot_date}</p>
          </div>
        </div>
        
        {appointment.status === 'booked' && (
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => navigate(`/patient/doctors/${appointment.doctor_id}/slots?reschedule=${appointmentId}`)}>
              <CalendarClock className="w-4 h-4 mr-2" /> Reschedule
            </Button>
            <Button variant="destructive" onClick={() => setIsCancelModalOpen(true)}>
              <XCircle className="w-4 h-4 mr-2" /> Cancel
            </Button>
          </div>
        )}
      </div>

      <Dialog open={isCancelModalOpen} onOpenChange={setIsCancelModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Appointment</DialogTitle>
            <DialogDescription>Are you sure you want to cancel this appointment? This action cannot be undone.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <p className="text-sm font-medium">Reason for cancellation (optional)</p>
              <Textarea 
                value={cancelReason} 
                onChange={(e) => setCancelReason(e.target.value)} 
                placeholder="Please let us know why you need to cancel..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCancelModalOpen(false)} disabled={isCancelling}>Keep Appointment</Button>
            <Button variant="destructive" onClick={handleCancel} disabled={isCancelling}>
              {isCancelling ? 'Cancelling...' : 'Yes, Cancel it'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Core Info */}
        <Card className="border-none shadow-sm h-fit">
          <CardHeader className="bg-slate-50 border-b">
            <CardTitle>Consultation Info</CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div>
              <p className="text-sm font-medium text-slate-500">Time</p>
              <p>{appointment.slot?.start_time.substring(0,5)} - {appointment.slot?.end_time.substring(0,5)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Status</p>
              <Badge variant="outline" className="mt-1 capitalize">{appointment.status}</Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Your Symptoms</p>
              <p className="whitespace-pre-wrap">{appointment.symptoms}</p>
            </div>
          </CardContent>
        </Card>

        {/* Consultation & Prescription Info */}
        {appointment.consultation && (
          <Card className="border-none shadow-sm h-fit">
            <CardHeader className="bg-purple-50 border-b border-purple-100 dark:bg-purple-900/20 dark:border-purple-900">
              <CardTitle className="flex items-center text-purple-800 dark:text-purple-300">
                <Pill className="h-5 w-5 mr-2" />
                Consultation & Prescription
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div>
                <p className="text-sm font-medium text-slate-500">Diagnosis</p>
                <p className="mt-1">{appointment.consultation.diagnosis || 'No formal diagnosis recorded'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">Clinical Notes</p>
                <p className="whitespace-pre-wrap mt-1">{appointment.consultation.notes}</p>
              </div>
              
              {appointment.consultation.prescription?.medications?.length > 0 && (
                <div className="pt-4 border-t mt-4">
                  <p className="text-sm font-medium text-slate-500 mb-3">Prescribed Medications</p>
                  <div className="space-y-3">
                    {appointment.consultation.prescription.medications.map((med: any, idx: number) => (
                      <div key={idx} className="bg-slate-50 dark:bg-slate-900 p-3 rounded-md text-sm border">
                        <p className="font-semibold">{med.name}</p>
                        <div className="grid grid-cols-2 gap-2 mt-2 text-slate-600 dark:text-slate-400">
                          <p><strong>Dosage:</strong> {med.dosage}</p>
                          <p><strong>Freq:</strong> {med.frequency}</p>
                          <p><strong>Duration:</strong> {med.duration}</p>
                          <p><strong>Period:</strong> {med.start_date} to {med.end_date}</p>
                        </div>
                        {med.instructions && (
                          <p className="mt-2 text-slate-500"><em>"{med.instructions}"</em></p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* AI Pre-Visit Summary */}
        <Card className="border-none shadow-sm h-fit">
          <CardHeader className="bg-blue-50 border-b border-blue-100 dark:bg-blue-900/20 dark:border-blue-900">
            <CardTitle className="flex items-center text-blue-800 dark:text-blue-300">
              <Activity className="h-5 w-5 mr-2" />
              AI Pre-Visit Summary
            </CardTitle>
            <CardDescription className="text-blue-600 dark:text-blue-400">
              Generated by AI for your doctor
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            {!appointment.ai_pre_visit_status || appointment.ai_pre_visit_status === 'skipped' ? (
              <p className="text-sm text-slate-500 text-center py-4">No summary generated.</p>
            ) : appointment.ai_pre_visit_status === 'processing' || appointment.ai_pre_visit_status === 'pending' ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-sm text-slate-500">AI is analyzing your symptoms...</p>
              </div>
            ) : appointment.ai_pre_visit_summary ? (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p><strong>Chief Complaint:</strong> {appointment.ai_pre_visit_summary.chief_complaint}</p>
                <p><strong>Urgency Level:</strong> {appointment.ai_pre_visit_summary.urgency_level}</p>
                <p><strong>Suggested Questions for Doctor:</strong></p>
                <ul className="list-disc pl-5">
                  {appointment.ai_pre_visit_summary.suggested_questions?.map((q: string, i: number) => (
                    <li key={i}>{q}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-sm text-slate-500 text-center py-4">Summary analysis failed.</p>
            )}
          </CardContent>
        </Card>

        {/* AI Post-Visit Summary (Only if completed) */}
        {appointment.status === 'completed' && appointment.ai_post_visit_status === 'completed' && appointment.ai_post_visit_summary && (
           <Card className="border-none shadow-sm h-fit md:col-span-2">
           <CardHeader className="bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-900">
             <CardTitle className="flex items-center text-emerald-800 dark:text-emerald-300">
               <FileText className="h-5 w-5 mr-2" />
               Post-Visit Summary & Instructions
             </CardTitle>
             <CardDescription className="text-emerald-600 dark:text-emerald-400">
               AI-generated summary of your consultation and care plan
             </CardDescription>
           </CardHeader>
           <CardContent className="pt-6">
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p><strong>Summary:</strong> {appointment.ai_post_visit_summary.patient_summary}</p>
                <p><strong>Follow-up Instructions:</strong> {appointment.ai_post_visit_summary.follow_up_instructions}</p>
                {appointment.ai_post_visit_summary.medication_schedule?.length > 0 && (
                  <>
                    <p><strong>Medication Schedule:</strong></p>
                    <ul className="list-disc pl-5">
                      {appointment.ai_post_visit_summary.medication_schedule.map((m: any, i: number) => (
                        <li key={i}>{m.time_of_day}: {m.medication_name} ({m.instructions})</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
           </CardContent>
         </Card>
        )}
      </div>
    </div>
  );
}
