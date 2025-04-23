import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sanvia-refreshToken');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  // console.log(`Token value: ${token}`);
  // console.log('Request Headers Before Sending:', config.headers);
  return config;
});

export const securityApi = {
  getEncryptionKey: async () => {
    try {
        const response = await api.get<{ "key": string }>('/get-encryption-key');
        return response.data.key;
      } catch (error) {
        console.error('Error destroying chat session:', error);
        throw error;
      }
  }
};

export default securityApi; 