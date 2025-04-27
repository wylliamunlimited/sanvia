import documentApi, { DocumentMetadata } from '../../../api/documentApi'
import { firestoreApi } from '../../../api/firestoreApi'

export type Document = DocumentMetadata

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB in bytes

export const fetchDocuments = async (): Promise<Document[]> => {
  try {
    const response = await documentApi.getAllDocuments()
    return response.documents
  } catch (err) {
    console.error('Error fetching documents:', err)
    throw new Error('Failed to load documents')
  }
}

export const uploadDocuments = async (files: File[]): Promise<DocumentMetadata[]> => {
  // Validate file sizes first
  const oversizedFiles = files.filter(file => file.size > MAX_FILE_SIZE)
  if (oversizedFiles.length > 0) {
    const fileNames = oversizedFiles.map(f => f.name).join(', ')
    throw new Error(`Files exceeding 5MB limit: ${fileNames}`)
  }

  try {
    return await Promise.all(files.map(file => documentApi.uploadDocument(file)))
  } catch (error) {
    console.error('Error uploading files:', error)
    throw new Error('Failed to upload one or more files')
  }
}

export const getPreviewUrl = async (documentId: string): Promise<string> => {
  try {
    const { signed_url } = await documentApi.getFreshSignedUrl(documentId)
    return signed_url
  } catch (err) {
    console.error('Error fetching preview URL:', err)
    throw new Error('Failed to load document preview')
  }
}

export const deleteDocument = async (documentId: string): Promise<void> => {
  try {
    const response = await firestoreApi.deleteDocument(documentId);
    if (!response.ok) {
      throw new Error('Failed to delete document');
    }
  } catch (error) {
    console.error('Error deleting document:', error);
    throw error;
  }
};