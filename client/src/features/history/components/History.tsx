import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './History.css'
import Header from '../../../shared/components/Header'
import { formatHistoryTime, groupSessionsByDate } from '../utils/dateUtils'
import { ChatSession, fetchChatThreads } from '../services/historyService'

const History = () => {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadChatThreads = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        const sessions = await fetchChatThreads()
        setChatSessions(sessions)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load chat history.')
      } finally {
        setIsLoading(false)
      }
    }
    
    loadChatThreads()
  }, [])

  // Handle navigation to chat thread
  const handleChatItemClick = (chatId: string) => {
    navigate(`/chat/${chatId}`)
  }

  const filteredSessions = chatSessions.filter(session =>
    session.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const groupedSessions = groupSessionsByDate(filteredSessions)

  return (
    <div className="history-content">
      <Header
        icon={<></>}
        title=""
      />

      <h2 className="history-subheader">Your chat history</h2>

      <div className="search-section">
        <div className="search-row">
          <div className="search-input-container">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button
                className="clear-search"
                onClick={() => setSearchQuery('')}
                aria-label="Clear search"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="history-area scrollable-area">
        {error && (
          <div className="error-message">{error}</div>
        )}
        {!isLoading && !error && (
          <div className="history-timeline">
            {Object.entries(groupedSessions).length > 0 ? (
              Object.entries(groupedSessions).map(([dateGroup, sessions]) => (
                <div key={dateGroup} className="history-group">
                  <div className="history-date-header">
                    {dateGroup}
                  </div>
                  {sessions.map(session => (
                    <div 
                      key={session.id} 
                      className="history-item"
                      onClick={() => handleChatItemClick(session.id)}
                    >
                      <div>
                        <div className="history-text">{session.title}</div>
                        <div className="history-time">{formatHistoryTime(session.timestamp)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ))
            ) : (
              <div className="no-results">
                {searchQuery ? 'There are no chats matching "' + searchQuery + '"' : 'You have no previous chats with Sanvia'}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default History