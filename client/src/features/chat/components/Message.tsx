import React from 'react';
import ReactMarkdown from 'react-markdown';
import { SourceItem } from '../../../api/chatApi';

interface MessageProps {
  id: number;
  text: string;
  isUser: boolean;
  sources?: SourceItem[];
  onSourcesClick: (messageId: number) => void;
}

const Message: React.FC<MessageProps> = ({ id, text, isUser, sources, onSourcesClick }) => {
  const renderMessageContent = () => {
    if (isUser) {
      // Don't apply Markdown to user messages
      return <div className="message-text">{text}</div>
    }
    
    // Apply Markdown to AI responses
    return (
      <div className="message-text markdown-content">
        <ReactMarkdown>{text}</ReactMarkdown>
      </div>
    )
  }

  return (
    <div className={`message ${isUser ? 'user' : 'ai'}`} data-message-id={id}>
      {renderMessageContent()}
      {!isUser && sources && sources.length > 0 && (
        <div className="message-sources">
          <button 
            className="sources-button"
            onClick={() => onSourcesClick(id)}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
            </svg>
            <span>Sources</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default Message; 