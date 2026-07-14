import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { doctorApi } from '../services/doctorApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { ArrowLeft, FileText, Activity, User } from 'lucide-react';

export function AppointmentView() {
  const { appointmentId } = useParams<{ appointmentId: string }>();
  const navigate = useNavigate();
  const [appointment, setAppointment] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (appointmentId) fetchAppointment();
  }, [appointmentId]);

  const fetchAppointment = async () => {
    setIsLoading(true);
    try {
      const data = await doctorApi.getAppointment(appointmentId!);
      setAppointment(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <div className="p-8 text-center">Loading details...</div>;
  if (!appointment) return <div className="p-8 text-center text-red-500">Appointment not found</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/doctor/appointments')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">Appointment Details</h1>
          <p className="text-slate-500">{appointment.slot?.slot_date} at {appointment.slot?.start_time.substring(0,5)}</p>
        </div>
        
        {appointment.status === 'booked' && (
          <Button 
            onClick={() => navigate(`/doctor/appointments/${appointment.id}/consultation`)}
          >
            Start Consultation
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Patient Profile */}
        <Card className="md:col-span-1 border-none shadow-sm h-fit">
          <CardHeader className="bg-slate-50 border-b">
            <CardTitle className="flex items-center">
              <User className="h-5 w-5 mr-2 text-slate-500" />
              Patient Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div>
              <p className="text-sm font-medium text-slate-500">Name</p>
              <p className="font-medium">{appointment.patient?.user?.full_name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Blood Group</p>
              <p>{appointment.patient?.blood_group || 'Not specified'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Medical History</p>
              <p className="text-sm">{appointment.patient?.medical_history || 'None reported'}</p>
            </div>
          </CardContent>
        </Card>

        {/* Clinical Info & Summaries */}
        <div className="md:col-span-2 space-y-6">
          <Card className="border-none shadow-sm">
            <CardHeader className="bg-slate-50 border-b">
              <CardTitle>Reported Symptoms</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <p className="whitespace-pre-wrap">{appointment.symptoms}</p>
            </CardContent>
          </Card>

          <Card className="border-none shadow-sm">
            <CardHeader className="bg-blue-50 border-b border-blue-100 dark:bg-blue-900/20 dark:border-blue-900">
              <CardTitle className="flex items-center text-blue-800 dark:text-blue-300">
                <Activity className="h-5 w-5 mr-2" />
                AI Pre-Visit Summary
              </CardTitle>
              <CardDescription className="text-blue-600 dark:text-blue-400">
                Extracted insights from patient symptoms
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              {!appointment.ai_pre_visit_status || appointment.ai_pre_visit_status === 'skipped' ? (
                <p className="text-sm text-slate-500 py-4">No summary generated.</p>
              ) : appointment.ai_pre_visit_status === 'processing' || appointment.ai_pre_visit_status === 'pending' ? (
                <p className="text-sm text-slate-500 py-4">Processing...</p>
              ) : appointment.ai_pre_visit_summary ? (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <p><strong>Chief Complaint:</strong> {appointment.ai_pre_visit_summary.chief_complaint}</p>
                  <p><strong>Urgency Level:</strong> {appointment.ai_pre_visit_summary.urgency_level}</p>
                  <p><strong>Suggested Questions:</strong></p>
                  <ul className="list-disc pl-5">
                    {appointment.ai_pre_visit_summary.suggested_questions?.map((q: string, i: number) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="text-sm text-slate-500 py-4">Summary analysis failed.</p>
              )}
            </CardContent>
          </Card>
          
          {appointment.status === 'completed' && appointment.ai_post_visit_status === 'completed' && appointment.ai_post_visit_summary && (
             <Card className="border-none shadow-sm h-fit">
             <CardHeader className="bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-900">
               <CardTitle className="flex items-center text-emerald-800 dark:text-emerald-300">
                 <FileText className="h-5 w-5 mr-2" />
                 Post-Visit Summary (Sent to Patient)
               </CardTitle>
             </CardHeader>
             <CardContent className="pt-6">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <p><strong>Summary:</strong> {appointment.ai_post_visit_summary.patient_summary}</p>
                  <p><strong>Follow-up Instructions:</strong> {appointment.ai_post_visit_summary.follow_up_instructions}</p>
                </div>
             </CardContent>
           </Card>
          )}
        </div>
      </div>
    </div>
  );
}
