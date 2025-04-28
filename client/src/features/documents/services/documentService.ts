import documentApi, { DocumentMetadata } from '../../../api/documentApi'
import { firestoreApi } from '../../../api/firestoreApi'

export type Document = DocumentMetadata

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB in bytes

export const fetchDocuments = async (): Promise<Document[]> => {
  try {
    const response = await documentApi.getAllDocuments();
    return response.documents;
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
};

export const uploadDocuments = async (files: File[]): Promise<Document[]> => {
  try {
    const uploadPromises = files.map(async (file) => {
      const response = await documentApi.uploadDocument(file);
      return {
        document_id: response.document_id,
        filename: response.filename,
        upload_date: response.upload_date,
        gcs_url: response.gcs_url,
        extracted_text: response.extracted_text
      };
    });
    return await Promise.all(uploadPromises);
  } catch (error) {
    console.error('Error uploading documents:', error);
    throw error;
  }
};

export const getPreviewUrl = async (documentId: string): Promise<string> => {
  try {
    const response = await documentApi.getFreshSignedUrl(documentId);
    return response.signed_url;
  } catch (error) {
    console.error('Error getting preview URL:', error);
    throw error;
  }
};

export const deleteDocument = async (documentId: string): Promise<void> => {
  try {
    await documentApi.deleteDocument(documentId);
  } catch (error) {
    // If the document is already deleted or not found, we can ignore the error
    // since the UI has already been updated
    if (error instanceof Error && error.message.includes('404')) {
      return;
    }
    throw error;
  }
};