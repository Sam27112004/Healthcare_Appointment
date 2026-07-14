import api from '../../../config/api';

export const appointmentApi = {
  getAppointments: async () => {
    const response = await api.get('/patients/me/appointments');
    return response.data;
  },

  getAvailableSlots: async (doctorId: string, dateStr: string) => {
    const response = await api.get(`/doctors/${doctorId}/slots`, {
      params: { date: dateStr }
    });
    return response.data; // List of slots
  },

  holdSlot: async (slotId: string) => {
    const response = await api.post('/appointments/hold', { slot_id: slotId });
    return response.data;
  },

  bookAppointment: async (slotId: string, symptoms: string) => {
    const response = await api.post('/appointments', {
      slot_id: slotId,
      symptoms: symptoms
    });
    return response.data;
  },

  getPreVisitSummary: async (appointmentId: string) => {
    const response = await api.get(`/appointments/${appointmentId}`);
    return response.data; // Return the full appointment which has pre_visit_summary
  }
};
