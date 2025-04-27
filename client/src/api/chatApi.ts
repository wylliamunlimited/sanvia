import axios from 'axios';
import { decryptAESGCM, encryptAESGCM } from './encryption/utils/encryption';

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
  // simple_response?: string;
  total_sources?: SourceItem[];
  sources?: SourceItem[];
  thread_id?: string;
}

export interface EncryptedChatResponse {
  chat: ChatMessage[];
  full_response?: {
    "ciphertext": string,
    "iv": string
  };
  // simple_response?: string;
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

      // const rawBody = JSON.stringify({});
      const aeskey = sessionStorage.getItem("AES_KEY");
      if (!aeskey) throw new Error("Encryption key missing");
      
      // NOTE: ENCRYPT
      console.log("Encrypting Message: ", prompt);
      const { ciphertext, iv } = await encryptAESGCM(JSON.stringify({ "prompt": prompt }), aeskey);

      const response = await api.post<EncryptedChatResponse>(`/sanvia-chat/${threadId}`, { 
        "encrypted_prompt": ciphertext, 
        "iv": iv 
      });

      // NOTE: DECRYPT
      let decryptedFullResonse = "";
      try {
        const encrypted = response.data.full_response;
        
        if (!encrypted || !encrypted.ciphertext || !encrypted.iv) throw new Error("Missing encrypted repsonse.")

        decryptedFullResonse = await decryptAESGCM(encrypted.ciphertext, encrypted.iv, aeskey);
      } catch (error) {
        console.log("Decryption failed: ", error);
        decryptedFullResonse = "[DECRYPTION FAILED]";
      }
      
      return {
        ...response.data,
        full_response: decryptedFullResonse
      };
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
  },

  deleteChatThread: async (thread_id: string): Promise<any> => {
    try {
      const response = await api.post<any>(`/delete-user-data/delete-individual-chat/${thread_id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting chat thread:', error);
      throw error;
    }
  }
};

export default chatApi; 
