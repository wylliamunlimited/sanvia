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

export interface ChatThread {
  thread_id: string;
  title: string;
  last_updated_at: string;
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
  createChat: async (): Promise<{ msg: string, thread_id: string }> => {
    try {
      const response = await api.post<{ msg: string, thread_id: string }>('/create-chat');
      return response.data;
    } catch (error) {
      console.error('Error creating chat:', error);
      throw error;
    }
  },
  
  sendMessageToThread: async (threadId: string, prompt: string): Promise<ChatResponse> => {
    try {
      const response = await api.post<ChatResponse>(`/sanvia-chat/${threadId}`, { prompt });
      return response.data;
    } catch (error) {
      console.error('Error sending message to thread:', error);
      throw error;
    }
  },
  
  getChatByThreadId: async (threadId: string): Promise<ChatResponse> => {
    try {
      const response = await api.get<ChatResponse>(`/chat/${threadId}`);
      return response.data;
    } catch (error) {
      console.error('Error retrieving chat:', error);
      throw error;
    }
  },

  getAllChatThreads: async (): Promise<ChatThread[]> => {
    try {
      const response = await api.get<{ threads: ChatThread[] }>('/chats');
      return response.data.threads;
    } catch (error) {
      console.error('Error fetching chat threads:', error);
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