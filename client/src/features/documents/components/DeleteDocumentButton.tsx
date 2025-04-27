import React, { useState } from 'react';
import { deleteDocument } from '../../profile/services/deleteService';
import './DeleteDocumentButton.css';

interface DeleteDocumentButtonProps {
  documentId: string;
  onDelete?: () => void;
}

const DeleteDocumentButton: React.FC<DeleteDocumentButtonProps> = ({ documentId, onDelete }) => {
  const [isConfirming, setIsConfirming] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleDeleteClick = () => {
    setIsConfirming(true);
  };

  const handleConfirmChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfirmationText(e.target.value);
  };

  const handleCancel = () => {
    setIsConfirming(false);
    setConfirmationText('');
    setError(null);
  };

  const handleConfirmDelete = async () => {
    if (confirmationText === 'DELETE') {
      try {
        await deleteDocument(documentId);
        setError(null);
        setIsConfirming(false);
        if (onDelete) {
          onDelete();
        }
      } catch (err) {
        setError('Failed to delete document. Please try again.');
      }
    }
  };

  if (isConfirming) {
    return (
      <div className="delete-document-confirmation">
        <input
          type="text"
          value={confirmationText}
          onChange={handleConfirmChange}
          placeholder="Type DELETE to confirm"
          className="confirmation-field"
        />
        <div className="confirmation-buttons">
          <button 
            className="confirm-button" 
            onClick={handleConfirmDelete}
            disabled={confirmationText !== 'DELETE'}
          >
            Confirm Delete
          </button>
          <button className="cancel-button" onClick={handleCancel}>
            Cancel
          </button>
        </div>
        {error && <div className="error-message">{error}</div>}
      </div>
    );
  }

  return (
    <button 
      className="delete-document-button"
      onClick={handleDeleteClick}
    >
      Delete Document
    </button>
  );
};

export default DeleteDocumentButton; 