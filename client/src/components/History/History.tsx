import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './History.css'
import Header from '../ui/Header'
import chatApi from '../../api/chatApi'

type ChatSession = {
  id: string;
  title: string;
  timestamp: Date;
}

const History = () => {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch chat threads on component mount
  useEffect(() => {
    const fetchChatThreads = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        const threads = await chatApi.getAllChatThreads()
        
        const sessions = threads.map(thread => ({
          id: thread.thread_id,
          title: thread.title || 'Untitled Chat',
          timestamp: new Date(thread.last_updated_at)
        }))
        
        setChatSessions(sessions)
      } catch (err) {
        console.error('Error fetching chat history:', err)
        setError('Failed to load chat history.')
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchChatThreads()
  }, [])

  // Handle navigation to chat thread
  const handleChatItemClick = (chatId: string) => {
    navigate(`/chat/${chatId}`)
  }

  const formatHistoryTime = (timestamp: Date) => {
    const now = new Date()
    const today = now.setHours(0, 0, 0, 0)
    const yesterday = today - 86400000
    
    const itemDate = new Date(timestamp).setHours(0, 0, 0, 0)
    const time = timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit'
    })

    if (itemDate === today) {
      return `Today at ${time}`
    } else if (itemDate === yesterday) {
      return `Yesterday at ${time}`
    } else {
      return `${timestamp.toLocaleDateString('en-US', { 
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })} at ${time}`
    }
  }

  const groupSessionsByDate = (sessions: ChatSession[]) => {
    const now = new Date()
    const today = now.setHours(0, 0, 0, 0)
    const yesterday = today - 86400000
    const oneWeekAgo = today - 86400000 * 7

    const grouped = sessions.reduce((groups, session) => {
      const timestamp = session.timestamp.getTime()
      const itemDate = new Date(session.timestamp).setHours(0, 0, 0, 0)
      
      let key
      if (itemDate === today) {
        key = 'Today'
      } else if (itemDate === yesterday) {
        key = 'Yesterday'
      } else if (timestamp > oneWeekAgo) {
        key = session.timestamp.toLocaleDateString('en-US', { weekday: 'long' })
      } else {
        key = session.timestamp.toLocaleDateString('en-US', { 
          month: 'short',
          year: 'numeric'
        })
      }
      
      if (!groups[key]) {
        groups[key] = {
          timestamp: itemDate,
          sessions: []
        }
      }
      groups[key].sessions.push(session)
      return groups
    }, {} as Record<string, { timestamp: number; sessions: ChatSession[] }>)

    // Sort sessions within each group by timestamp (newest first)
    Object.values(grouped).forEach(group => {
      group.sessions.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    })

    // Convert to array and sort groups by timestamp (newest first)
    return Object.entries(grouped)
      .sort(([, a], [, b]) => b.timestamp - a.timestamp)
      .reduce((obj, [key, value]) => {
        obj[key] = value.sessions
        return obj
      }, {} as Record<string, ChatSession[]>)
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

      <div className="history-area">
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