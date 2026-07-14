import { useState, useEffect } from 'react';
import { adminApi } from '../services/adminApi';
import { Card, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Textarea } from '../../../components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { toast } from '../../../hooks/use-toast';
import { Plus, Edit2, Trash2, Activity, Loader2 } from 'lucide-react';

export function SpecializationManagement() {
  const [specializations, setSpecializations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetchSpecializations();
  }, []);

  const fetchSpecializations = async () => {
    setIsLoading(true);
    try {
      const data = await adminApi.getSpecializations();
      setSpecializations(data.items || []);
    } catch (e) {
      toast({ variant: 'destructive', title: 'Error', description: 'Failed to load specializations' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = (spec?: any) => {
    if (spec) {
      setEditingId(spec.id);
      setFormData({ name: spec.name, description: spec.description || '' });
    } else {
      setEditingId(null);
      setFormData({ name: '', description: '' });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      if (editingId) {
        await adminApi.updateSpecialization(editingId, formData);
        toast({ title: 'Success', description: 'Specialization updated successfully' });
      } else {
        await adminApi.createSpecialization(formData);
        toast({ title: 'Success', description: 'Specialization created successfully' });
      }
      setIsModalOpen(false);
      fetchSpecializations();
    } catch (err: any) {
      toast({ variant: 'destructive', title: 'Error', description: err.response?.data?.detail || 'Operation failed' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this specialization?')) return;
    try {
      await adminApi.deleteSpecialization(id);
      toast({ title: 'Success', description: 'Specialization deleted' });
      fetchSpecializations();
    } catch (err: any) {
      toast({ variant: 'destructive', title: 'Error', description: err.response?.data?.detail || 'Failed to delete' });
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">Medical Specializations</h1>
          <p className="text-slate-500">Manage all doctor specializations in the system.</p>
        </div>
        <Button onClick={() => handleOpenModal()} className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md">
          <Plus className="w-4 h-4 mr-2" /> Add Specialization
        </Button>
      </div>

      <Card className="border-0 shadow-lg bg-white/60 backdrop-blur-xl">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center text-slate-500 flex flex-col items-center">
              <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-600" />
              Loading specializations...
            </div>
          ) : specializations.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              <Activity className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p>No specializations found. Add one to get started.</p>
            </div>
          ) : (
            <div className="divide-y">
              {specializations.map((spec) => (
                <div key={spec.id} className="p-6 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{spec.name}</h3>
                    <p className="text-sm text-slate-500 mt-1">{spec.description || 'No description provided.'}</p>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" onClick={() => handleOpenModal(spec)}>
                      <Edit2 className="w-4 h-4 mr-1" /> Edit
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(spec.id)}>
                      <Trash2 className="w-4 h-4 mr-1" /> Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingId ? 'Edit Specialization' : 'Add Specialization'}</DialogTitle>
            <DialogDescription>
              Provide the name and description for this medical specialization.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="e.g., Cardiology" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} placeholder="Brief description of the specialization..." rows={3} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)} disabled={isSaving}>Cancel</Button>
              <Button type="submit" disabled={isSaving}>
                {isSaving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving...</> : 'Save'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
