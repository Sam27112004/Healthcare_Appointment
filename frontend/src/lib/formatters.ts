import { format, parseISO } from 'date-fns';

/**
 * Formats a raw date string (e.g. "2024-10-15") into "Oct 15, 2024"
 */
export const formatDate = (dateString?: string): string => {
  if (!dateString) return 'N/A';
  try {
    return format(parseISO(dateString), 'MMM d, yyyy');
  } catch (e) {
    return dateString;
  }
};

/**
 * Formats a raw time string (e.g. "14:30:00") into "02:30 PM"
 */
export const formatTime = (timeString?: string): string => {
  if (!timeString) return 'N/A';
  try {
    // Prefix with a dummy date to parse the time
    const dummyDate = `2000-01-01T${timeString}`;
    return format(parseISO(dummyDate), 'hh:mm a');
  } catch (e) {
    return timeString.substring(0, 5); // Fallback to "14:30"
  }
};

/**
 * Returns a human-readable string for the appointment status
 */
export const formatStatus = (status?: string): string => {
  if (!status) return 'Unknown';
  switch (status.toLowerCase()) {
    case 'scheduled': return 'Scheduled';
    case 'completed': return 'Completed';
    case 'cancelled': return 'Cancelled';
    case 'no_show': return 'No Show';
    default: return status.charAt(0).toUpperCase() + status.slice(1);
  }
};
