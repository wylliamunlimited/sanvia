import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './Chat.css'
import { getScrollbarWidth } from '../../utils/scrollbar'
import chatApi, { SourceItem } from '../../api/chatApi'
import Header from '../ui/Header'
import SourcesSidebar from './SourcesSidebar'
import Message from './Message'

type Message = {
  id: number
  text: string
  isUser: boolean
  sources?: SourceItem[]
}

const Chat = () => {
  const { threadId } = useParams<{ threadId: string }>()
  const navigate = useNavigate()
  
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedMessageId, setSelectedMessageId] = useState<number | null>(null)
  const [isSourcesSidebarOpen, setIsSourcesSidebarOpen] = useState(false)
  const [showAllSources, setShowAllSources] = useState(false)
  
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messageAreaRef = useRef<HTMLDivElement>(null)
  const prevMessageCountRef = useRef(0)

  // Store threadId in localStorage whenever it changes
  useEffect(() => {
    if (threadId) {
      localStorage.setItem('lastChatId', threadId);
    }
  }, [threadId]);

  // Get chat by threadId
  useEffect(() => {
    const loadChat = async () => {
      if (threadId) {
        try {
          setIsLoading(true);
          const chatData = await chatApi.getChatByThreadId(threadId);
          
          if (chatData.chat && chatData.chat.length > 0) {
            // Filter out system messages
            const filteredMessages = chatData.chat.filter(msg => msg.role !== 'system');
            
            const convertedMessages = filteredMessages.map((msg, index) => ({
              id: Date.now() + index,
              text: msg.content,
              isUser: msg.role === 'user',
              sources: msg.role === 'assistant' ? msg.references : undefined
            }));
            
            setMessages(convertedMessages);
          }
        } catch (err) {
          console.error('Error loading chat:', err);
          setError('Failed to load chat history.');
        } finally {
          setIsLoading(false);
        }
      } else {
        setMessages([]);
      }
    };
    
    loadChat();
  }, [threadId]);

  // Auto-adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputText])

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

  // Set scrollbar width for consistent scrollbar width
  useEffect(() => {
    document.documentElement.style.setProperty('--scrollbar-width', `${getScrollbarWidth()}px`)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || isThinking) return
    
    // Clear any previous errors
    setError(null)

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: inputText,
      isUser: true
    }
    setMessages(prev => [...prev, userMessage])
    
    // Clear input and set thinking state
    setInputText('')
    setIsThinking(true)
    setShouldAutoScroll(true)

    try {
      if (!threadId) {
        // Create new thread on generic /chat route
        const createResponse = await chatApi.createChat()
        const newThreadId = createResponse.thread_id
        
        // Send message to new thread
        const response = await chatApi.sendMessageToThread(newThreadId, inputText.trim())
        
        // Update URL to new thread
        navigate(`/chat/${newThreadId}`, { replace: true })
        
        // Filter and add AI response to chat
        const assistantMessages = response.chat.filter(msg => msg.role === 'assistant')
        if (assistantMessages.length > 0) {
          const lastAssistantMessage = assistantMessages[assistantMessages.length - 1]
          setMessages(prev => [...prev, {
            id: Date.now(),
            text: lastAssistantMessage.content,
            isUser: false,
            sources: lastAssistantMessage.references
          }])
        }
      } else {
        // Send message to existing thread
        const response = await chatApi.sendMessageToThread(threadId, inputText.trim())
        
        // Filter and add AI response to chat
        const assistantMessages = response.chat.filter(msg => msg.role === 'assistant')
        if (assistantMessages.length > 0) {
          const lastAssistantMessage = assistantMessages[assistantMessages.length - 1]
          setMessages(prev => [...prev, {
            id: Date.now(),
            text: lastAssistantMessage.content,
            isUser: false,
            sources: lastAssistantMessage.references
          }])
        }
      }
    } catch (err) {
      console.error('Error sending message:', err)
      setError('Failed to get response. Please try again.')
      
      // Add error message to chat
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Sorry, I'm having trouble connecting to the server. Please try again later.",
        isUser: false
      }])
    } finally {
      setIsThinking(false)
    }
  }

  const handleScroll = () => {
    if (messageAreaRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messageAreaRef.current;
      const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) < 10;
      
      // Only update if value actually changed
      if (shouldAutoScroll !== isAtBottom) {
        setShouldAutoScroll(isAtBottom);
      }
    }
  }

  const handleSourcesClick = (messageId: number) => {
    if (selectedMessageId === messageId && isSourcesSidebarOpen && !showAllSources) {
      setIsSourcesSidebarOpen(false);
    } else {
      setSelectedMessageId(messageId);
      setShowAllSources(false);
      setIsSourcesSidebarOpen(true);
    }
  }

  const handleAllSourcesClick = () => {
    if (isSourcesSidebarOpen && showAllSources) {
      setIsSourcesSidebarOpen(false);
    } else {
      setShowAllSources(true);
      setIsSourcesSidebarOpen(true);
    }
  }

  const closeSidebar = () => {
    setIsSourcesSidebarOpen(false);
  }

  // Get sources based on current mode
  const selectedMessageSources = showAllSources
    ? messages
        .flatMap(msg => msg.sources || [])
        // Remove duplicate sources
        .filter((source, index, self) => 
          index === self.findIndex(s => s.url === source.url)
        )
    : messages.find(msg => msg.id === selectedMessageId)?.sources || [];

  return (
    <div className={`chat-content ${isSourcesSidebarOpen ? 'sidebar-open' : ''}`}>
      <Header 
        icon={
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        }
        title="Chat"
      />

      <div 
        ref={messageAreaRef}
        className="message-area"
        onScroll={handleScroll}
      >
        {!isLoading && messages.map(message => (
          <Message
            key={message.id}
            id={message.id}
            text={message.text}
            isUser={message.isUser}
            sources={message.sources}
            onSourcesClick={handleSourcesClick}
          />
        ))}
        {isThinking && (
          <div className="thinking-indicator">
            Thinking...
          </div>
        )}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-area">
        <div className="input-container">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                if (!isThinking && !isLoading) handleSubmit(e)
              }
            }}
            placeholder="Reply to Sanvia..."
            rows={1}
            disabled={isLoading}
          />
          <button 
            type="button" 
            className="sources-all-button"
            onClick={handleAllSourcesClick}
            aria-label="Show all sources"
            style={{ display: messages.some(msg => msg.sources && msg.sources.length > 0) ? 'flex' : 'none' }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
            </svg>
          </button>
          <button type="submit" disabled={isThinking || isLoading}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L12 20M12 2L5 9M12 2L19 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </form>
      
      <div className="disclaimer">
        For informational purposes only. Not a substitute for professional medical advice.
      </div>

      <SourcesSidebar 
        isOpen={isSourcesSidebarOpen}
        sources={selectedMessageSources}
        onClose={closeSidebar}
        showAllSources={showAllSources}
      />
    </div>
  )
}

export default Chat