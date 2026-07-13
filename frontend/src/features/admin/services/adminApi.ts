import api from '../../../config/api';

export const adminApi = {
  getDoctors: async () => {
    const response = await api.get('/admin/doctors');
    return response.data;
  },

  createDoctor: async (data: any) => {
    const response = await api.post('/admin/doctors', data);
    return response.data;
  },

  getSpecializations: async () => {
    const response = await api.get('/admin/specializations');
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/admin/stats');
    return response.data;
  },
  
  createSchedule: async (doctorId: string, data: any) => {
    const response = await api.post(`/admin/doctors/${doctorId}/schedule`, data);
    return response.data;
  },
  
  createLeave: async (doctorId: string, date: string, reason: string) => {
    const response = await api.post(`/admin/doctors/${doctorId}/leave`, {
      leave_date: date,
      reason
    });
    return response.data;
  }
};
