import { useState, useEffect } from 'react';
import { patientApi } from '../services/patientApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../../config/routes';

interface Doctor {
  id: string;
  user_id: string;
  user: {
    full_name: string;
  };
  specialization_id: string;
  specialization: {
    name: string;
  };
  qualifications: string;
  experience_years: number;
}

export function DoctorSearch() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [specializations, setSpecializations] = useState<{ id: string, name: string }[]>([]);
  const [search, setSearch] = useState('');
  const [selectedSpec, setSelectedSpec] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    fetchSpecializations();
    fetchDoctors();
  }, []);

  const fetchSpecializations = async () => {
    try {
      const data = await patientApi.getSpecializations();
      setSpecializations(data.items || data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDoctors = async () => {
    setIsLoading(true);
    try {
      const data = await patientApi.getDoctors({
        search: search || undefined,
        specialization_id: selectedSpec === "all" ? undefined : (selectedSpec || undefined),
      });
      setDoctors(data.items || data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDoctors();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Find a Doctor</h1>
        <p className="text-slate-500">Search by name or filter by specialization to book an appointment.</p>
      </div>

      <Card className="border-none shadow-sm">
        <CardContent className="p-6">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search doctors by name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="w-full md:w-64">
              <Select value={selectedSpec} onValueChange={setSelectedSpec}>
                <SelectTrigger>
                  <SelectValue placeholder="All Specializations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Specializations</SelectItem>
                  {specializations.map((spec) => (
                    <SelectItem key={spec.id} value={spec.id}>
                      {spec.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit">Search</Button>
          </form>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="text-center py-12">Loading doctors...</div>
      ) : doctors.length === 0 ? (
        <div className="text-center py-12 text-slate-500">No doctors found matching your criteria.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {doctors.map((doc) => (
            <Card key={doc.id} className="overflow-hidden hover:shadow-md transition-shadow">
              <CardHeader className="bg-slate-50 border-b pb-4">
                <CardTitle className="text-xl">Dr. {doc.user?.full_name}</CardTitle>
                <CardDescription>
                  <Badge variant="secondary" className="mt-1">
                    {doc.specialization?.name}
                  </Badge>
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div>
                  <p className="text-sm font-medium text-slate-500">Qualifications</p>
                  <p className="text-sm">{doc.qualifications}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Experience</p>
                  <p className="text-sm">{doc.experience_years} years</p>
                </div>
                <Button 
                  className="w-full mt-2" 
                  onClick={() => navigate(`/patient/doctors/${doc.id}/slots`)}
                >
                  Book Appointment
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
