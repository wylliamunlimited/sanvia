import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  role: string;
  content: string;
  references?: SourceItem[];
}

export interface SourceItem {
  title: string;
  url: string;
  content?: string;
  score?: number;
  categories?: string[];
}

export interface ChatResponse {
  chat: ChatMessage[];
  full_response?: string;
  simple_response?: string;
  total_sources?: SourceItem[];
  sources?: SourceItem[];
  thread_id?: string;
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

      console.log("response data: ", response.data);

      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
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