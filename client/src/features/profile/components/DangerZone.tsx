import React, { useState } from 'react';
import './DangerZone.css';

const DangerZone: React.FC = () => {
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [isConfirmingDocuments, setIsConfirmingDocuments] = useState(false);
  const [isConfirmingChats, setIsConfirmingChats] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');

  const handleDeleteClick = () => {
    setIsConfirmingDelete(true);
    setIsConfirmingDocuments(false);
    setIsConfirmingChats(false);
  };

  const handleDocumentsClick = () => {
    setIsConfirmingDocuments(true);
    setIsConfirmingDelete(false);
    setIsConfirmingChats(false);
  };

  const handleChatsClick = () => {
    setIsConfirmingChats(true);
    setIsConfirmingDelete(false);
    setIsConfirmingDocuments(false);
  };

  const handleConfirmChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfirmationText(e.target.value);
  };

  const handleCancel = () => {
    setIsConfirmingDelete(false);
    setIsConfirmingDocuments(false);
    setIsConfirmingChats(false);
    setConfirmationText('');
  };

  const handleConfirmDelete = () => {
    if (confirmationText === 'DELETE') {
      // TODO: Implement account deletion logic
      console.log('Account deletion confirmed');
    }
  };

  const handleConfirmDocuments = () => {
    if (confirmationText === 'DELETE') {
      // TODO: Implement documents deletion logic
      console.log('Documents deletion confirmed');
    }
  };

  const handleConfirmChats = () => {
    if (confirmationText === 'DELETE') {
      // TODO: Implement chats deletion logic
      console.log('Chats deletion confirmed');
    }
  };

  const renderConfirmationUI = (onConfirm: () => void) => (
    <div className="confirmation-container">
      <div className="confirmation-input">
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
            onClick={onConfirm}
            disabled={confirmationText !== 'DELETE'}
          >
            Confirm Delete
          </button>
          <button className="cancel-button" onClick={handleCancel}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <h3 className="danger-zone-header">Danger zone</h3>
      <p className="danger-zone-description">
        These actions are irreversible. Please proceed with caution.
      </p>
      <div className="danger-zone">
        <div className="danger-zone-item">
          <div className="danger-info">
            <span className="danger-name">Delete all chats</span>
            <p className="danger-description">
              Permanently delete all your chat history and conversations.
            </p>
          </div>
          {!isConfirmingChats ? (
            <button className="danger-button" onClick={handleChatsClick}>
              Delete all chats
            </button>
          ) : (
            renderConfirmationUI(handleConfirmChats)
          )}
        </div>

        <div className="danger-zone-item">
          <div className="danger-info">
            <span className="danger-name">Delete all documents</span>
            <p className="danger-description">
              Permanently delete all your documents and associated data.
            </p>
          </div>
          {!isConfirmingDocuments ? (
            <button className="danger-button" onClick={handleDocumentsClick}>
              Delete all documents
            </button>
          ) : (
            renderConfirmationUI(handleConfirmDocuments)
          )}
        </div>

        <div className="danger-zone-item">
          <div className="danger-info">
            <span className="danger-name">Delete your account</span>
            <p className="danger-description">
              Permanently delete your account and all associated data.
            </p>
          </div>
          {!isConfirmingDelete ? (
            <button className="danger-button" onClick={handleDeleteClick}>
              Delete account
            </button>
          ) : (
            renderConfirmationUI(handleConfirmDelete)
          )}
        </div>
      </div>
    </>
  );
};

export default DangerZone; 