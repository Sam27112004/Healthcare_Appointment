import { useState, useEffect } from 'react';
import { adminApi } from '../services/adminApi';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Textarea } from '../../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';

interface DoctorOnboardingModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function DoctorOnboardingModal({ open, onOpenChange, onSuccess }: DoctorOnboardingModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [specializations, setSpecializations] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    specialization_id: '',
    qualification: '',
    experience_years: '',
    bio: '',
    consultation_fee: ''
  });

  useEffect(() => {
    if (open) {
      fetchSpecializations();
    }
  }, [open]);

  const fetchSpecializations = async () => {
    try {
      const data = await adminApi.getSpecializations();
      setSpecializations(data.items || data);
    } catch (e) {
      console.error('Failed to load specializations', e);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (value: string) => {
    setFormData({ ...formData, specialization_id: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const payload: any = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        specialization_id: formData.specialization_id,
      };

      if (formData.phone) payload.phone = formData.phone;
      if (formData.qualification) payload.qualification = formData.qualification;
      if (formData.experience_years && !isNaN(parseInt(formData.experience_years))) {
        payload.experience_years = parseInt(formData.experience_years);
      }
      if (formData.bio) payload.bio = formData.bio;
      if (formData.consultation_fee && !isNaN(parseFloat(formData.consultation_fee))) {
        payload.consultation_fee = parseFloat(formData.consultation_fee);
      }

      await adminApi.createDoctor(payload);
      
      // Reset form on success
      setFormData({
        email: '', password: '', full_name: '', phone: '',
        specialization_id: '', qualification: '', experience_years: '',
        bio: '', consultation_fee: ''
      });
      onSuccess();
      onOpenChange(false);
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;
      let errMsg = 'Failed to create doctor';
      if (typeof detail === 'string') {
        errMsg = detail;
      } else if (Array.isArray(detail)) {
        errMsg = detail[0]?.msg || errMsg;
      }
      alert(errMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Onboard New Doctor</DialogTitle>
          <DialogDescription>
            Create a new doctor account and profile.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name *</Label>
              <Input id="full_name" name="full_name" value={formData.full_name} onChange={handleChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input id="email" type="email" name="email" value={formData.email} onChange={handleChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password *</Label>
              <Input id="password" type="password" name="password" value={formData.password} onChange={handleChange} required minLength={8} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input id="phone" name="phone" value={formData.phone} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="specialization">Specialization *</Label>
              <Select value={formData.specialization_id} onValueChange={handleSelectChange} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select Specialization" />
                </SelectTrigger>
                <SelectContent>
                  {specializations.map((spec) => (
                    <SelectItem key={spec.id} value={spec.id}>
                      {spec.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="qualification">Qualification</Label>
              <Input id="qualification" name="qualification" value={formData.qualification} onChange={handleChange} placeholder="e.g. MD, MBBS" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="experience_years">Experience (Years)</Label>
              <Input id="experience_years" type="number" name="experience_years" value={formData.experience_years} onChange={handleChange} min="0" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="consultation_fee">Consultation Fee ($)</Label>
              <Input id="consultation_fee" type="number" step="0.01" name="consultation_fee" value={formData.consultation_fee} onChange={handleChange} min="0" />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="bio">Bio</Label>
            <Textarea id="bio" name="bio" value={formData.bio} onChange={handleChange} rows={3} />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Creating...' : 'Create Doctor'}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
