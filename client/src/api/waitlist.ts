import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface WaitlistEntry {
  name: string;
  email: string;
  company?: string;
  role?: string;
}

export const submitWaitlist = async (entry: WaitlistEntry) => {
  try {
    const response = await axios.post(`${API_URL}/waitlist/submit`, entry);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Failed to submit to waitlist');
    }
    throw error;
  }
}; 