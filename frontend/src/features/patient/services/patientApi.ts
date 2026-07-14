import api from '../../../config/api';

export const patientApi = {
  getDoctors: async (params?: { specialization_id?: string; search?: string }) => {
    const response = await api.get('/doctors', { params });
    return response.data; // { items: Doctor[], total: number }
  },

  getDoctor: async (doctorId: string) => {
    const response = await api.get(`/doctors/${doctorId}`);
    return response.data;
  },

  getSpecializations: async () => {
    const response = await api.get('/specializations');
    return response.data;
  }
};
