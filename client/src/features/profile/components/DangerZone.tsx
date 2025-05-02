import React, { useState } from 'react';
import './DangerZone.css';
import { deleteAccount, deleteAllChats, deleteAllDocuments } from '../services/deleteService';
import { useFirebase } from '../../../context/FirebaseContext';

const DangerZone: React.FC = () => {
  const { auth } = useFirebase();
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [isConfirmingDocuments, setIsConfirmingDocuments] = useState(false);
  const [isConfirmingChats, setIsConfirmingChats] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [error, setError] = useState<string | null>(null);

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
    setError(null);
  };

  const handleConfirmDelete = async () => {
    if (confirmationText === 'DELETE') {
      try {
        await deleteAccount();
        // Sign out from Firebase
        await auth.signOut();
        // Clear any local storage or session data
        localStorage.clear();
        sessionStorage.clear();
        // Redirect to landing page
        window.location.href = '/';
      } catch (err) {
        setError('Failed to delete account. Please try again.');
      }
    }
  };

  const handleConfirmDocuments = async () => {
    if (confirmationText === 'DELETE') {
      try {
        await deleteAllDocuments();
        setError(null);
        handleCancel();
      } catch (err) {
        setError('Failed to delete documents. Please try again.');
      }
    }
  };

  const handleConfirmChats = async () => {
    if (confirmationText === 'DELETE') {
      try {
        await deleteAllChats();
        setError(null);
        handleCancel();
      } catch (err) {
        setError('Failed to delete chats. Please try again.');
      }
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
      {error && <div className="error-message">{error}</div>}
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