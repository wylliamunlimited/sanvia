import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './NewChat.css'
import { getScrollbarWidth } from '../utils/scrollbar'
import chatApi from '../../../api/chatApi'
import Header from '../../../shared/components/Header'
import { useProfile } from '../../../context/ProfileContext'

const NewChat = () => {
  const navigate = useNavigate()
  const { userData } = useProfile()
  const [inputText, setInputText] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const getTimeOfDay = (): string => {
    const hour = new Date().getHours()
    if (hour >= 5 && hour < 12) return 'morning'
    if (hour >= 12 && hour < 18) return 'afternoon'
    return 'evening'
  }

  // Auto-adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputText])

  // Set scrollbar width for consistent scrollbar width
  useEffect(() => {
    document.documentElement.style.setProperty('--scrollbar-width', `${getScrollbarWidth()}px`)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || isThinking) return
    
    // Clear any previous errors
    setError(null)
    
    // Set thinking state
    setIsThinking(true)

    try {
      // Create new thread
      const createResponse = await chatApi.createChat()
      const newThreadId = createResponse.thread_id
      
      // Send message to new thread
      await chatApi.sendMessageToThread(newThreadId, inputText.trim())
      
      // Navigate to thread chat view
      navigate(`/chat/${newThreadId}`, { replace: true })
    } catch (err) {
      console.error('Error starting chat:', err)
      setError('Failed to start a new chat. Please try again.')
      setIsThinking(false)
    }
  }

  return (
    <div className="new-chat-content">
      <Header
        icon={<></>}
        title=""
      />

      <div className="new-chat-container">
        <div className="new-chat-message">
          <h2>Good {getTimeOfDay()}, {userData.firstName}</h2>
          <p>How can I help with your health related questions?</p>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
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
              placeholder="Ask a health question"  // "Ask Sanvia about health topics, symptoms, or wellness advice...""
              rows={1}
            />
            <button type="submit" disabled={isThinking}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L12 20M12 2L5 9M12 2L19 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </form>
        
        {isThinking && (
          <div className="thinking-indicator">
            Starting a new chat...
          </div>
        )}
      </div>
      
      <div className="disclaimer">
        For informational purposes only. Not a substitute for professional medical advice.
      </div>
    </div>
  )
}

export default NewChat 