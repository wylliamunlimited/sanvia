import React from 'react';
import './DeleteDocumentButton.css';

interface DeleteDocumentButtonProps {
  documentId: string;
  onDelete?: () => void;
}

const DeleteDocumentButton: React.FC<DeleteDocumentButtonProps> = ({ documentId, onDelete }) => {
  const handleDelete = () => {
    if (onDelete) {
      onDelete();
    }
  };

  return (
    <button 
      className="delete-button"
      onClick={handleDelete}
      aria-label={`Delete document ${documentId}`}
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
      </svg>
    </button>
  );
};

export default DeleteDocumentButton; 