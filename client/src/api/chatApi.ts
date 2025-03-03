import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TEST_AUTH_TOKEN = import.meta.env.VITE_TEST_AUTH_TOKEN;  // Testing

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatResponse {
  chat: ChatMessage[];
}

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

export const chatApi = {
  sendMessage: async (prompt: string): Promise<ChatResponse> => {
    try {
      const response = await api.post<ChatResponse>('/ai-response', { prompt });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Testing with hardcoded auth token
  testSendMessage: async (prompt: string): Promise<ChatResponse> => {
    try {
      const response = await axios.post<ChatResponse>(`${API_URL}/ai-response`, 
        { prompt },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${TEST_AUTH_TOKEN}`
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error sending test message:', error);
      throw error;
    }
  },

  destroySession: async (): Promise<{ msg: string }> => {
    try {
      const response = await api.post<{ msg: string }>('/destroy-chat-session');
      return response.data;
    } catch (error) {
      console.error('Error destroying chat session:', error);
      throw error;
    }
  }
};

export default chatApi; 