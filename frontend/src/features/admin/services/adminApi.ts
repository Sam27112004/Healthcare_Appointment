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

  createSpecialization: async (data: { name: string, description?: string }) => {
    const response = await api.post('/admin/specializations', data);
    return response.data;
  },

  updateSpecialization: async (id: string, data: { name: string, description?: string }) => {
    const response = await api.put(`/admin/specializations/${id}`, data);
    return response.data;
  },

  deleteSpecialization: async (id: string) => {
    const response = await api.delete(`/admin/specializations/${id}`);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  getSchedule: async (doctorId: string) => {
    const response = await api.get(`/admin/doctors/${doctorId}/schedule`);
    return response.data;
  },
  
  createSchedule: async (doctorId: string, data: any) => {
    const response = await api.post(`/admin/doctors/${doctorId}/schedule`, data);
    return response.data;
  },
  
  generateSlots: async (doctorId: string, startDate: string, endDate: string) => {
    const response = await api.post(`/admin/doctors/${doctorId}/slots/generate`, {
      start_date: startDate,
      end_date: endDate
    });
    return response.data;
  },
  
  createLeave: async (doctorId: string, date: string, reason: string) => {
    const response = await api.post(`/admin/doctors/${doctorId}/leave`, {
      leave_date: date,
      reason
    });
    return response.data;
  },

  getAllAppointments: async (params?: { skip?: number, limit?: number, status?: string }) => {
    const response = await api.get('/admin/appointments', { params });
    return response.data;
  }
};
