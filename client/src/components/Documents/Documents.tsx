import { useState, useEffect } from 'react'
import './Documents.css'
import Header from '../ui/Header'
import documentApi, { DocumentMetadata } from '../../api/documentApi'

type Document = DocumentMetadata

const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await documentApi.getAllDocuments()
        setDocuments(response.documents)
      } catch (err) {
        console.error('Error fetching documents:', err)
        setError('Failed to load documents. Please refresh the page.')
      }
    }

    fetchDocuments()
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

    try {
      const newDocuments = await Promise.all(files.map(async file => {
        try {
          return await documentApi.uploadDocument(file)
        } catch (err) {
          console.error(`Error uploading ${file.name}:`, err)
          throw new Error(`Failed to upload ${file.name}`)
        }
      }))

      setDocuments(prev => [...prev, ...newDocuments])
    } catch (err) {
      console.error('Error handling files:', err)
      setError('Failed to upload one or more files. Please try again.')
    }
  }

  const handlePreview = async (doc: Document) => {
    try {
      const { signed_url } = await documentApi.getFreshSignedUrl(doc.document_id)
      setPreviewUrl(signed_url)
      setPreviewDoc(doc)
    } catch {
      setError('Failed to load document preview. Please try again.')
    }
  }

  const closePreview = () => {
    setPreviewDoc(null)
    setPreviewUrl(null)
  }

  return (
    <div className="documents-content">
      <Header 
        icon={
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        }
        title="Documents"
      />

      <div className="documents-area">
        <div 
          className={`upload-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
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
            />
            Choose files
          </label>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="documents-list">
          {documents.map(doc => (
            <div 
              key={doc.document_id} 
              className="document-item"
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
                <iframe 
                  src={previewUrl ?? ''} 
                  title={previewDoc.filename}
                  width="100%"
                  height="100%"
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