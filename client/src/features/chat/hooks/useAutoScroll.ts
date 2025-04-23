import { useEffect, useRef } from 'react';

interface UseAutoScrollProps {
  messages: any[];
  shouldAutoScroll: boolean;
  setShouldAutoScroll: (value: boolean) => void;
}

export const useAutoScroll = ({ messages, shouldAutoScroll, setShouldAutoScroll }: UseAutoScrollProps) => {
  const messageAreaRef = useRef<HTMLDivElement>(null);
  const prevMessageCountRef = useRef(0);

  // Auto-scroll when new messages are added
  useEffect(() => {
    const hasNewMessage = messages.length > prevMessageCountRef.current;
    prevMessageCountRef.current = messages.length;
    
    // Only scroll when new message and auto-scroll enabled
    if (hasNewMessage && shouldAutoScroll && messageAreaRef.current) {
      setTimeout(() => {
        // Find last user message
        const userMessages = messages.filter(msg => msg.isUser);
        const lastUserMessage = userMessages[userMessages.length - 1];
        
        // Scroll to user message
        if (lastUserMessage) {
          const userElement = document.querySelector(`.message.user[data-message-id="${lastUserMessage.id}"]`);
          if (userElement) {
            userElement.scrollIntoView({ 
              behavior: 'smooth', 
              block: 'start' 
            });
          }
        }
      }, 150);
    }
  }, [messages.length, shouldAutoScroll]);

  const handleScroll = () => {
    if (messageAreaRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messageAreaRef.current;
      const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) < 10;
      
      // Only update if value actually changed
      if (shouldAutoScroll !== isAtBottom) {
        setShouldAutoScroll(isAtBottom);
      }
    }
  };

  return {
    messageAreaRef,
    handleScroll
  };
}; 