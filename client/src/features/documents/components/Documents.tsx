import { useState, useEffect } from 'react'
import './Documents.css'
import { getScrollbarWidth } from '../../../shared/utils/scrollbar'
import { Document, fetchDocuments, uploadDocuments, getPreviewUrl, deleteDocument } from '../services/documentService'
import DeleteDocumentButton from './DeleteDocumentButton'
import Header from "../../../shared/components/Header";

const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isIframeLoaded, setIsIframeLoaded] = useState(false)

  useEffect(() => {
    document.documentElement.style.setProperty('--scrollbar-width', `${getScrollbarWidth()}px`)
  }, [])

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const docs = await fetchDocuments()
        setDocuments(docs)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load documents. Please refresh the page.')
      }
    }

    loadDocuments()
  }, [])

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : []
    handleFiles(files)
  }

  const handleFiles = async (files: File[]) => {
    setError(null)
    setIsUploading(true)

    try {
      const newDocuments = await uploadDocuments(files)
      setDocuments(prev => [...prev, ...newDocuments])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload one or more files. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handlePreview = async (doc: Document) => {
    try {
      setIsIframeLoaded(false)
      setPreviewDoc(doc)
      const signedUrl = await getPreviewUrl(doc.document_id)
      setPreviewUrl(signedUrl)
    } catch {
      setError('Failed to load document preview. Please try again.')
      setPreviewDoc(null)
      setPreviewUrl(null)
    }
  }

  const handleIframeLoad = () => {
    setTimeout(() => {
      setIsIframeLoaded(true)
    }, 500)
  }

  const closePreview = () => {
    setPreviewDoc(null)
    setPreviewUrl(null)
    setIsIframeLoaded(false)
  }

  const handleDeleteDocument = async (documentId: string) => {
    try {
      // First remove from UI
      setDocuments(prev => prev.filter(doc => doc.document_id !== documentId));
      if (previewDoc?.document_id === documentId) {
        closePreview();
      }
      // Then attempt to delete from backend
      try {
        await deleteDocument(documentId);
      } catch (error) {
        // If the document is already deleted or not found, we can ignore the error
        // since the UI has already been updated
        if (!(error instanceof Error) || !error.message.includes('404')) {
          setError('Failed to delete document. Please try again.');
        }
      }
    } catch (err) {
      // Only show error if it's not a 404
      if (!(err instanceof Error) || !err.message.includes('404')) {
        setError('Failed to delete document. Please try again.');
      }
    }
  }

  return (
    <div className="documents-content">

<div className="documents-subheader">
       <Header
          icon={
            <svg className="documents-logo" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#757575" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
          }
          title="Documents"
        />
      </div>
      
      <div 
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <>
            <svg className="spinner" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
            </svg>
            <p>Uploading files...</p>
          </>
        ) : (
          <>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p>Drag and drop files here or</p>
            <label className="upload-button">
              <input 
                type="file" 
                multiple
                onChange={handleFileInput}
                accept=".pdf"
                disabled={isUploading}
              />
              Choose files
            </label>
          </>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="documents-area scrollable-area">
        <div className="documents-list">
          {documents.map(doc => (
            <div 
              key={doc.document_id} 
              className="document-item"
            >
              <div 
                className="document-content"
                onClick={() => handlePreview(doc)}
              >
                <div className="document-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                </div>
                <div className="document-info">
                  <div className="document-name">{doc.filename}</div>
                  <div className="document-meta">
                    {new Date(doc.upload_date).toLocaleDateString()}
                  </div>
                </div>
              </div>
              <DeleteDocumentButton 
                documentId={doc.document_id}
                onDelete={() => handleDeleteDocument(doc.document_id)}
              />
            </div>
          ))}
        </div>

        {previewDoc && (
          <div className="preview-modal">
            <div className="preview-content">
              <div className="preview-header">
                <h3>{previewDoc.filename}</h3>

                <button 
                  className="preview-close-button"
                  onClick={closePreview}
                  aria-label="Close preview"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              <div className="preview-body">
                <div className={`preview-loading ${isIframeLoaded ? 'hidden' : ''}`}>
                  <svg className="spinner" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                  </svg>
                  <p>Loading preview...</p>
                </div>
                <iframe 
                  src={previewUrl ?? ''} 
                  title={previewDoc.filename}
                  width="100%"
                  height="100%"
                  className={isIframeLoaded ? 'loaded' : ''}
                  onLoad={handleIframeLoad}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Documents 