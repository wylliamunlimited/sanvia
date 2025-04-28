import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface DocumentMetadata {
  filename: string;
  document_id: string;
  upload_date: string;
  gcs_url: string;
  extracted_text: string;
}

interface DocumentsResponse {
  documents: DocumentMetadata[];
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
  return config;
});

export const documentApi = {
  uploadDocument: async (file: File): Promise<DocumentMetadata> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post<DocumentMetadata>('/upload-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  },

  getDocument: async (documentId: string): Promise<Blob> => {
    try {
      const response = await api.get(`/document/${documentId}`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching document:', error);
      throw error;
    }
  },

  getAllDocuments: async (): Promise<DocumentsResponse> => {
    try {
      const response = await api.get<DocumentsResponse>('/documents');
      return response.data;
    } catch (error) {
      console.error('Error fetching all documents:', error);
      throw error;
    }
  },

  getFreshSignedUrl: async (documentId: string): Promise<{ signed_url: string; expires_in: number }> => {
    try {
      const response = await api.get(`/document/${documentId}/signed-url`);
      return response.data;
    } catch (error) {
      console.error('Error getting fresh signed URL:', error);
      throw error;
    }
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    try {
      await api.post(`/delete-user-data/delete-document/${documentId}`);
    } catch (error) {
      // If the document is already deleted or not found, we can ignore the error
      // since the UI has already been updated
      if (error instanceof Error && error.message.includes('404')) {
        return;
      }
      console.error('Error deleting document:', error);
      throw error;
    }
  }
};

export default documentApi; 