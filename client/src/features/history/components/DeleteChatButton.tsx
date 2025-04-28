import React from 'react';
import { deleteIndividualChat } from '../services/historyService';
import './DeleteChatButton.css';

interface DeleteChatButtonProps {
  chatId: string;
  onDelete?: () => void;
}

const DeleteChatButton: React.FC<DeleteChatButtonProps> = ({ chatId, onDelete }) => {
  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the chat item click
    try {
      await deleteIndividualChat(chatId);
      if (onDelete) {
        onDelete();
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  return (
    <button 
      className="delete-button"
      onClick={handleDelete}
      aria-label="Delete chat"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
      </svg>
    </button>
  );
};

export default DeleteChatButton; 