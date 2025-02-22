import { useState, useRef, useEffect } from 'react'
import './Chat.css'
import { getScrollbarWidth } from '../../utils/scrollbar'

type Message = {
  id: number
  text: string
  isUser: boolean
}

const SAMPLE_AI_RESPONSE = `Lorem ipsum dolor sit amet, consectetur adipiscing elit...`

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true)
  
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messageAreaRef = useRef<HTMLDivElement>(null)

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || isThinking) return

    setMessages(prev => [...prev, { 
      id: Date.now(), 
      text: inputText,
      isUser: true
    }])
    
    setInputText('')
    setIsThinking(true)
    setShouldAutoScroll(true)

    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: SAMPLE_AI_RESPONSE,
        isUser: false
      }])
      setIsThinking(false)
    }, 2000)
  }

  const handleScroll = () => {
    if (messageAreaRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messageAreaRef.current
      setShouldAutoScroll(scrollHeight - (scrollTop + clientHeight) < 100)
    }
  }

  return (
    <div className="chat-content">
      <div className="chat-header">
        <div className="header-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <h2>Chat</h2>
        </div>
      </div>

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
            {message.text}
          </div>
        ))}
        {isThinking && (
          <div className="thinking-indicator">
            Thinking...
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
    </div>
  )
}

export default Chat 