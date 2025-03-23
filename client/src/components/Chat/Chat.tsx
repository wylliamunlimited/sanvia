import { useState, useRef, useEffect } from 'react'
import './Chat.css'
import { getScrollbarWidth } from '../../utils/scrollbar'
import chatApi from '../../api/chatApi'
import ReactMarkdown from 'react-markdown'
import Header from '../ui/Header'

type Message = {
  id: number
  text: string
  isUser: boolean
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messageAreaRef = useRef<HTMLDivElement>(null)

  // Load initial greeting message
  useEffect(() => {
    setMessages([{
      id: Date.now(),
      text: "Hello! How can I help with your health related questions?",
      isUser: false
    }])
  }, [])

  // Auto-adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputText])

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (shouldAutoScroll && messageAreaRef.current) {
      messageAreaRef.current.scrollTo({
        top: messageAreaRef.current.scrollHeight,
        behavior: messages.length ? 'smooth' : 'auto'
      })
    }
  }, [messages, isThinking, shouldAutoScroll])

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
      const response = await chatApi.sendMessage(inputText.trim())  // Change to chatApi.sendMessage once auth is implemented
      // Find last assistant message in chat history
      const assistantMessages = response.chat.filter(msg => msg.role === 'assistant')
      if (assistantMessages.length > 0) {
        const lastAssistantMessage = assistantMessages[assistantMessages.length - 1]
        
        // Add AI response to chat
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: lastAssistantMessage.content,
          isUser: false
        }])
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
      const { scrollTop, scrollHeight, clientHeight } = messageAreaRef.current
      setShouldAutoScroll(scrollHeight - (scrollTop + clientHeight) < 100)
    }
  }

  // Render message content with Markdown
  const renderMessageContent = (text: string, isUser: boolean) => {
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
    <div className="chat-content">
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
        {messages.map(message => (
          <div 
            key={message.id} 
            className={`message ${message.isUser ? 'user' : 'ai'}`}
          >
            {renderMessageContent(message.text, message.isUser)}
          </div>
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
                if (!isThinking) handleSubmit(e)
              }
            }}
            placeholder="Message Sanvia"
            rows={1}
          />
          <button type="submit" disabled={isThinking}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L12 20M12 2L5 9M12 2L19 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </form>
      
      <div className="disclaimer">
        For informational purposes only. Not a substitute for professional medical advice.
      </div>
    </div>
  )
}

export default Chat