import { create } from 'zustand';
import { appointmentApi } from '../features/patient/services/appointmentApi';

interface Slot {
  id: string;
  doctor_id: string;
  slot_date: string;
  start_time: string;
  end_time: string;
  status: string;
}

interface AppointmentState {
  selectedSlot: Slot | null;
  heldSlotId: string | null;
  holdExpiresAt: Date | null;
  symptoms: string;
  bookingNotes: string;
  isLoading: boolean;
  error: string | null;

  holdSlot: (slot: Slot) => Promise<void>;
  releaseHold: () => void;
  setSymptoms: (symptoms: string) => void;
  confirmBooking: () => Promise<any>;
  resetBookingFlow: () => void;
}

export const useAppointmentStore = create<AppointmentState>((set, get) => ({
  selectedSlot: null,
  heldSlotId: null,
  holdExpiresAt: null,
  symptoms: '',
  bookingNotes: '',
  isLoading: false,
  error: null,

  holdSlot: async (slot: Slot) => {
    set({ isLoading: true, error: null });
    try {
      const heldSlotData = await appointmentApi.holdSlot(slot.id);
      
      // We expect heldSlotData to have hold_expires_at
      let expiresAt = null;
      if (heldSlotData.held_until) {
         expiresAt = new Date(heldSlotData.held_until + "Z"); // Ensure UTC parsing
      } else {
         // Fallback 10 mins
         expiresAt = new Date(Date.now() + 10 * 60000);
      }

      set({
        selectedSlot: slot,
        heldSlotId: heldSlotData.id,
        holdExpiresAt: expiresAt,
        isLoading: false,
      });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to hold slot' 
      });
      throw error;
    }
  },

  releaseHold: () => {
    // In a real app we might call an API to release it early, 
    // but the system auto-cleans it up. For frontend, we just drop it.
    set({
      selectedSlot: null,
      heldSlotId: null,
      holdExpiresAt: null,
      symptoms: '',
    });
  },

  setSymptoms: (symptoms: string) => {
    set({ symptoms });
  },

  confirmBooking: async () => {
    const state = get();
    if (!state.heldSlotId) throw new Error("No slot held");

    set({ isLoading: true, error: null });
    try {
      const appointment = await appointmentApi.bookAppointment(state.heldSlotId, state.symptoms);
      set({ isLoading: false });
      return appointment;
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to confirm booking' 
      });
      throw error;
    }
  },

  resetBookingFlow: () => {
    set({
      selectedSlot: null,
      heldSlotId: null,
      holdExpiresAt: null,
      symptoms: '',
      bookingNotes: '',
      error: null,
    });
  }
}));
