import { useState, useEffect } from 'react';
import { adminApi } from '../services/adminApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { DoctorOnboardingModal } from '../components/DoctorOnboardingModal';

export function DoctorManagement() {
  const [doctors, setDoctors] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      const data = await adminApi.getDoctors();
      setDoctors(data.items || data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Doctors</h1>
          <p className="text-slate-500">Manage hospital medical staff.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" /> Add Doctor
        </Button>
      </div>

      <DoctorOnboardingModal 
        open={isModalOpen} 
        onOpenChange={setIsModalOpen} 
        onSuccess={fetchDoctors} 
      />

      <Card>
        <CardHeader>
          <CardTitle>Medical Staff</CardTitle>
          <CardDescription>All registered doctors in the system.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-slate-500">Loading doctors...</div>
          ) : doctors.length === 0 ? (
            <div className="text-center py-12 text-slate-500">No doctors registered.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Specialization</TableHead>
                  <TableHead>Experience</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {doctors.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">Dr. {doc.user?.full_name}</TableCell>
                    <TableCell>{doc.user?.email}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{doc.specialization?.name}</Badge>
                    </TableCell>
                    <TableCell>{doc.experience_years} years</TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button variant="outline" size="sm" onClick={() => navigate(`/admin/doctors/${doc.id}/schedule`)}>
                        Schedule
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => navigate(`/admin/doctors/${doc.id}/leaves`)}>
                        Leaves
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
