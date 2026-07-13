import api from '../../../config/api';

export const patientApi = {
  getDoctors: async (params?: { specialization?: string; search?: string }) => {
    const response = await api.get('/patient/doctors', { params });
    return response.data; // { items: Doctor[], total: number }
  },

  getDoctor: async (doctorId: string) => {
    const response = await api.get(`/patient/doctors/${doctorId}`);
    return response.data;
  },

  getSpecializations: async () => {
    const response = await api.get('/patient/specializations');
    return response.data;
  }
};
