import { useState, useEffect } from 'react';
import { patientApi } from '../services/patientApi';
import { useAuthStore } from '../../../stores/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Textarea } from '../../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { toast } from '../../../hooks/use-toast';
import { User, HeartPulse, Activity, Phone, MapPin, CalendarDays, Loader2 } from 'lucide-react';

export function PatientProfile() {
  const { user } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    date_of_birth: '',
    gender: '',
    blood_group: '',
    address: '',
    medical_history: '',
    phone: '',
    full_name: '',
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await patientApi.getProfile();
      setFormData({
        date_of_birth: data.date_of_birth || '',
        gender: data.gender || '',
        blood_group: data.blood_group || '',
        address: data.address || '',
        medical_history: data.medical_history || '',
        phone: data.user?.phone || '',
        full_name: data.user?.full_name || user?.full_name || '',
      });
    } catch (e) {
      console.error('Failed to load profile', e);
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to load profile data',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      const payload: any = {};
      if (formData.full_name) payload.full_name = formData.full_name;
      if (formData.phone) payload.phone = formData.phone;
      if (formData.date_of_birth) payload.date_of_birth = formData.date_of_birth;
      if (formData.gender) payload.gender = formData.gender;
      if (formData.blood_group) payload.blood_group = formData.blood_group;
      if (formData.address) payload.address = formData.address;
      if (formData.medical_history) payload.medical_history = formData.medical_history;

      await patientApi.updateProfile(payload);
      
      toast({
        title: 'Success',
        description: 'Your profile has been updated.',
      });
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;
      let errMsg = 'Failed to update profile';
      if (typeof detail === 'string') {
        errMsg = detail;
      } else if (Array.isArray(detail)) {
        errMsg = detail[0]?.msg || errMsg;
      }
      toast({
        variant: 'destructive',
        title: 'Update Failed',
        description: errMsg,
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="flex flex-col items-center space-y-4 text-slate-500">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">Patient Profile</h1>
        <p className="text-slate-500 mt-2">Manage your personal information and medical history.</p>
      </div>

      <Card className="border-0 shadow-lg bg-white/60 backdrop-blur-xl">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100 rounded-t-xl pb-6">
          <CardTitle className="flex items-center text-blue-900">
            <User className="mr-2 h-5 w-5 text-blue-600" /> Personal Information
          </CardTitle>
          <CardDescription>
            This information is shared with your doctors when you book an appointment.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6 pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                  <Input id="full_name" name="full_name" value={formData.full_name} onChange={handleChange} className="pl-9" placeholder="John Doe" required />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Input value={user?.email || ''} className="bg-slate-50 pl-3" disabled />
                </div>
                <p className="text-xs text-slate-400">Email cannot be changed.</p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                  <Input id="phone" name="phone" value={formData.phone} onChange={handleChange} className="pl-9" placeholder="+1 (555) 000-0000" />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="date_of_birth">Date of Birth</Label>
                <div className="relative">
                  <CalendarDays className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                  <Input id="date_of_birth" type="date" name="date_of_birth" value={formData.date_of_birth} onChange={handleChange} className="pl-9" />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select value={formData.gender} onValueChange={(v) => handleSelectChange('gender', v)}>
                  <SelectTrigger id="gender">
                    <SelectValue placeholder="Select Gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Male">Male</SelectItem>
                    <SelectItem value="Female">Female</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                    <SelectItem value="Prefer not to say">Prefer not to say</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="blood_group">Blood Group</Label>
                <div className="relative">
                  <HeartPulse className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 z-10" />
                  <Select value={formData.blood_group} onValueChange={(v) => handleSelectChange('blood_group', v)}>
                    <SelectTrigger id="blood_group" className="pl-9">
                      <SelectValue placeholder="Select Blood Group" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="A+">A+</SelectItem>
                      <SelectItem value="A-">A-</SelectItem>
                      <SelectItem value="B+">B+</SelectItem>
                      <SelectItem value="B-">B-</SelectItem>
                      <SelectItem value="O+">O+</SelectItem>
                      <SelectItem value="O-">O-</SelectItem>
                      <SelectItem value="AB+">AB+</SelectItem>
                      <SelectItem value="AB-">AB-</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Address</Label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Textarea id="address" name="address" value={formData.address} onChange={handleChange} className="pl-9 min-h-[80px]" placeholder="Full residential address" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="medical_history" className="flex items-center text-rose-700">
                <Activity className="mr-2 h-4 w-4" /> Medical History & Allergies
              </Label>
              <Textarea 
                id="medical_history" 
                name="medical_history" 
                value={formData.medical_history} 
                onChange={handleChange} 
                className="min-h-[120px] border-rose-200 focus-visible:ring-rose-500" 
                placeholder="List any chronic conditions, previous surgeries, or known allergies..." 
              />
              <p className="text-xs text-slate-500">This helps doctors prepare for your consultations effectively.</p>
            </div>
            
          </CardContent>
          <CardFooter className="bg-slate-50 border-t rounded-b-xl px-6 py-4 flex justify-end">
            <Button type="submit" disabled={isSaving} className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md hover:shadow-lg transition-all">
              {isSaving ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving Changes...</> : 'Save Profile'}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
