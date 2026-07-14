import api from '../../../config/api';

export const doctorApi = {
  getAppointments: async (params?: { date?: string; status?: string }) => {
    const response = await api.get('/doctor/appointments', { params });
    return response.data; // { items: Appointment[], total: number }
  },

  getAppointment: async (appointmentId: string) => {
    const response = await api.get(`/appointments/${appointmentId}`);
    return response.data; // Full appointment with summaries and symptoms
  },

  submitConsultation: async (appointmentId: string, diagnosis: string, notes: string) => {
    const response = await api.post(`/doctor/appointments/${appointmentId}/consultation`, {
      diagnosis,
      notes
    });
    return response.data;
  },

  submitPrescription: async (appointmentId: string, notes: string, medications: any[]) => {
    const response = await api.post(`/doctor/appointments/${appointmentId}/prescription`, {
      notes,
      medications
    });
    return response.data;
  },

  completeAppointment: async (appointmentId: string) => {
    const response = await api.post(`/doctor/appointments/${appointmentId}/complete`);
    return response.data;
  }
};
