import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { doctorApi } from '../services/doctorApi';

import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Textarea } from '../../../components/ui/textarea';
import { Label } from '../../../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Plus, Trash2 } from 'lucide-react';

export function ConsultationForm() {
  const { appointmentId } = useParams<{ appointmentId: string }>();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('notes');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form for Consultation Notes
  const { 
    register: registerNotes, 
    handleSubmit: handleNotesSubmit,
    formState: { errors: notesErrors }
  } = useForm({
    defaultValues: {
      diagnosis: '',
      notes: ''
    }
  });

  // Form for Prescription
  const {
    register: registerPrescription,
    control: prescriptionControl,
    handleSubmit: handlePrescriptionSubmit
  } = useForm({
    defaultValues: {
      prescriptionNotes: '',
      medications: [{ name: '', dosage: '', frequency: '', duration: '' }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control: prescriptionControl,
    name: 'medications'
  });

  const onNotesSubmit = async () => {
    setActiveTab('prescription');
  };

  const onFinalSubmit = async (prescriptionData: any) => {
    setIsSubmitting(true);
    setError(null);
    try {
      // We need the data from the first form too. In a real app we'd use a unified form state or store,
      // but since we are doing sequential submissions to different endpoints based on the API docs:
      
      // We'll just grab the values directly from the DOM for simplicity in this demo,
      // or we can use the backend's complete appointment flow.
      const diagnosis = (document.getElementById('diagnosis') as HTMLInputElement).value;
      const notes = (document.getElementById('notes') as HTMLTextAreaElement).value;

      // 1. Submit Consultation
      await doctorApi.submitConsultation(appointmentId!, diagnosis, notes);

      // 2. Submit Prescription
      if (prescriptionData.medications[0].name !== '') {
        await doctorApi.submitPrescription(
          appointmentId!, 
          prescriptionData.prescriptionNotes, 
          prescriptionData.medications
        );
      }

      // 3. Mark Complete (Triggers AI summary)
      await doctorApi.completeAppointment(appointmentId!);

      navigate(`/doctor/appointments/${appointmentId}`);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to submit consultation');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Conduct Consultation</h1>
        <p className="text-slate-500">Record diagnosis, notes, and prescriptions.</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="notes">1. Consultation Notes</TabsTrigger>
          <TabsTrigger value="prescription">2. Prescription</TabsTrigger>
        </TabsList>

        <TabsContent value="notes">
          <form onSubmit={handleNotesSubmit(onNotesSubmit)}>
            <Card>
              <CardHeader>
                <CardTitle>Clinical Notes</CardTitle>
                <CardDescription>Record your findings and primary diagnosis.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="diagnosis">Primary Diagnosis <span className="text-red-500">*</span></Label>
                  <Input id="diagnosis" {...registerNotes('diagnosis', { required: 'Diagnosis is required' })} />
                  {notesErrors.diagnosis && <p className="text-sm text-red-500">{notesErrors.diagnosis.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="notes">Clinical Notes <span className="text-red-500">*</span></Label>
                  <Textarea id="notes" rows={8} {...registerNotes('notes', { required: 'Notes are required' })} />
                  {notesErrors.notes && <p className="text-sm text-red-500">{notesErrors.notes.message}</p>}
                </div>
              </CardContent>
              <CardFooter className="flex justify-end">
                <Button type="submit">Next: Prescription</Button>
              </CardFooter>
            </Card>
          </form>
        </TabsContent>

        <TabsContent value="prescription">
          <form onSubmit={handlePrescriptionSubmit(onFinalSubmit)}>
            <Card>
              <CardHeader>
                <CardTitle>Prescription Builder</CardTitle>
                <CardDescription>Add medications and usage instructions.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">Medications</h3>
                    <Button 
                      type="button" 
                      variant="outline" 
                      size="sm" 
                      onClick={() => append({ name: '', dosage: '', frequency: '', duration: '' })}
                    >
                      <Plus className="h-4 w-4 mr-2" /> Add Medication
                    </Button>
                  </div>

                  {fields.map((field, index) => (
                    <div key={field.id} className="flex gap-4 items-start p-4 bg-slate-50 border rounded-lg">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 flex-1">
                        <div className="space-y-2">
                          <Label>Medicine Name</Label>
                          <Input {...registerPrescription(`medications.${index}.name` as const)} placeholder="e.g. Amoxicillin" />
                        </div>
                        <div className="space-y-2">
                          <Label>Dosage</Label>
                          <Input {...registerPrescription(`medications.${index}.dosage` as const)} placeholder="e.g. 500mg" />
                        </div>
                        <div className="space-y-2">
                          <Label>Frequency</Label>
                          <Input {...registerPrescription(`medications.${index}.frequency` as const)} placeholder="e.g. Twice a day" />
                        </div>
                        <div className="space-y-2">
                          <Label>Duration</Label>
                          <Input {...registerPrescription(`medications.${index}.duration` as const)} placeholder="e.g. 5 days" />
                        </div>
                      </div>
                      <Button 
                        type="button" 
                        variant="ghost" 
                        size="icon" 
                        className="text-red-500 mt-6"
                        onClick={() => remove(index)}
                        disabled={fields.length === 1}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>

                <div className="space-y-2 pt-4 border-t">
                  <Label>Additional Prescription Notes / Advice</Label>
                  <Textarea {...registerPrescription('prescriptionNotes')} placeholder="Drink plenty of water..." />
                </div>

                {error && (
                  <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
                    {error}
                  </div>
                )}
                
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button type="button" variant="outline" onClick={() => setActiveTab('notes')}>Back to Notes</Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Completing Consultation...' : 'Complete Consultation'}
                </Button>
              </CardFooter>
            </Card>
          </form>
        </TabsContent>
      </Tabs>
    </div>
  );
}
