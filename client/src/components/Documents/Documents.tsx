import { useState } from 'react'
import './Documents.css'

type Document = {
  id: number
  name: string
  uploadDate: Date
  size: string
  content?: string // For text files
  url?: string    // For PDFs and other files
}

const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null)

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
    const newDocuments = await Promise.all(files.map(async file => {
      const doc: Document = {
        id: Date.now(),
        name: file.name,
        uploadDate: new Date(),
        size: formatFileSize(file.size)
      }

      // Create preview URL for PDFs
      if (file.type === 'application/pdf') {
        doc.url = URL.createObjectURL(file)
      }
      // Read text files
      else if (file.type === 'text/plain') {
        doc.content = await file.text()
      }

      return doc
    }))

    setDocuments(prev => [...prev, ...newDocuments])
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) 
      return bytes + ' B'
    else if (bytes < 1024 * 1024) 
      return (bytes / 1024).toFixed(1) + ' KB'
    else 
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const handleDelete = (id: number) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id))
  }

  const handlePreview = (doc: Document) => {
    setPreviewDoc(doc)
  }

  const closePreview = () => {
    setPreviewDoc(null)
  }

  return (
    <div className="documents-content">
      <div className="chat-header">
        <div className="header-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <h2>Documents</h2>
        </div>
      </div>

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
              accept=".pdf,.doc,.docx,.txt"
            />
            Choose files
          </label>
        </div>

        <div className="documents-list">
          {documents.map(doc => (
            <div 
              key={doc.id} 
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
                <div className="document-name">{doc.name}</div>
                <div className="document-meta">
                  {doc.size} • {doc.uploadDate.toLocaleDateString()}
                </div>
              </div>
              <button 
                className="delete-button"
                onClick={(e) => {
                  e.stopPropagation()
                  handleDelete(doc.id)
                }}
                aria-label="Delete document"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
          ))}
        </div>

        {previewDoc && (
          <div className="preview-modal">
            <div className="preview-content">
              <div className="preview-header">
                <h3>{previewDoc.name}</h3>
                <button 
                  className="close-button"
                  onClick={closePreview}
                  aria-label="Close preview"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              <div className="preview-body">
                {previewDoc.url ? (
                  <iframe 
                    src={previewDoc.url} 
                    title={previewDoc.name}
                    width="100%"
                    height="100%"
                  />
                ) : previewDoc.content ? (
                  <pre>{previewDoc.content}</pre>
                ) : (
                  <div className="preview-unsupported">
                    This file type cannot be previewed
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Documents 