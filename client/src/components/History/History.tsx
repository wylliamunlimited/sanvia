import { useState, useEffect } from 'react'
import './History.css'
import { getScrollbarWidth } from '../../utils/scrollbar'

type HistoryType = 'conversation' | 'upload' | 'remove' | 'update'

type HistoryItem = {
  id: number
  type: HistoryType
  text: string
  timestamp: Date
}

const History = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'conversation' | 'context'>('all')
  const [history] = useState<HistoryItem[]>([
    {
      id: 1,
      type: 'conversation',
      text: 'Asked about persistent headaches. Described pattern: 2-3 times per week, throbbing pain, worse with light. Discussed possible migraine triggers and lifestyle factors.',
      timestamp: new Date('2025-02-18T10:30:00')
    },
    {
      id: 2,
      type: 'upload',
      text: 'Uploaded previous_neurologist_report.pdf',
      timestamp: new Date('2025-02-18T10:33:00')
    },
    {
      id: 3,
      type: 'conversation',
      text: 'Reviewed neurologist report. Confirmed migraine diagnosis. Discussed preventive medications and recommended keeping a headache diary.',
      timestamp: new Date('2025-02-18T10:33:01')
    },
    {
      id: 4,
      type: 'update',
      text: 'Updated medication list and treatment plan',
      timestamp: new Date('2025-02-18T10:37:00')
    },
    {
      id: 5,
      type: 'conversation',
      text: 'Followed up about medication side effects. Reported improved headache frequency but mild nausea. Adjusted dosing schedule to take with food.',
      timestamp: new Date('2025-02-17T10:40:00')
    },
    {
      id: 6,
      type: 'upload',
      text: 'Uploaded blood_pressure_readings.pdf',
      timestamp: new Date('2024-12-15T14:30:00')
    },
    {
      id: 7,
      type: 'conversation',
      text: 'Analyzed BP readings. Showing elevated patterns in morning. Discussed salt intake, stress management, and exercise routine adjustments.',
      timestamp: new Date('2024-12-15T14:30:01')
    },
    {
      id: 8,
      type: 'conversation',
      text: 'Discussed recent anxiety symptoms affecting sleep. Recommended mindfulness techniques, sleep hygiene improvements, and regular exercise.',
      timestamp: new Date('2024-11-20T09:15:00')
    }
  ])

  const filteredHistory = history.filter(item => {
    const matchesSearch = item.text.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = filterType === 'all' || 
      (filterType === 'conversation' && item.type === 'conversation') ||
      (filterType === 'context' && item.type !== 'conversation')
    return matchesSearch && matchesType
  })

  const groupHistoryByDate = (items: HistoryItem[]) => {
    const now = new Date()
    const today = now.setHours(0, 0, 0, 0)
    const yesterday = today - 86400000 // 24 hours in milliseconds
    const oneWeekAgo = today - 86400000 * 7

    const grouped = items.reduce((groups, item) => {
      const timestamp = item.timestamp.getTime()
      const itemDate = new Date(item.timestamp).setHours(0, 0, 0, 0)
      
      let key
      if (itemDate === today) {
        key = 'Today'
      } else if (itemDate === yesterday) {
        key = 'Yesterday'
      } else if (timestamp > oneWeekAgo) {
        key = item.timestamp.toLocaleDateString('en-US', { weekday: 'long' })
      } else {
        key = item.timestamp.toLocaleDateString('en-US', { 
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        })
      }
      
      if (!groups[key]) {
        groups[key] = []
      }
      groups[key].push(item)
      return groups
    }, {} as Record<string, HistoryItem[]>)

    // Sort items within each group by timestamp (newest first)
    Object.keys(grouped).forEach(key => {
      grouped[key].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    })

    return grouped
  }

  const groupedHistory = groupHistoryByDate(filteredHistory)

  const getIcon = (type: HistoryType) => {
    switch (type) {
      case 'conversation':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        )
      case 'upload':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        )
      case 'remove':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 6h18"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        )
      case 'update':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
          </svg>
        )
    }
  }

  const formatHistoryTime = (timestamp: Date) => {
    const now = new Date()
    const today = now.setHours(0, 0, 0, 0)
    const yesterday = today - 86400000
    const oneWeekAgo = today - 86400000 * 7
    
    const itemDate = new Date(timestamp).setHours(0, 0, 0, 0)
    const time = timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit'
    })

    if (itemDate === today) {
      return `Today at ${time}`
    } else if (itemDate === yesterday) {
      return `Yesterday at ${time}`
    } else if (timestamp.getTime() > oneWeekAgo) {
      return `${timestamp.toLocaleDateString('en-US', { weekday: 'long' })} at ${time}`
    } else {
      return `${timestamp.toLocaleDateString('en-US', { 
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })} at ${time}`
    }
  }

  useEffect(() => {
    document.documentElement.style.setProperty('--scrollbar-width', `${getScrollbarWidth()}px`)
  }, [])

  return (
    <div className="history-content">
      <div className="chat-header">
        <div className="header-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 8v4l3 3"/>
            <circle cx="12" cy="12" r="9"/>
          </svg>
          <h2>History</h2>
        </div>
      </div>

      <div className="search-section">
        <div className="search-row">
          <div className="search-input-container">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              placeholder="Search history..."
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

          <div className="filter-container">
            <select 
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as 'all' | 'conversation' | 'context')}
              className="filter-select"
            >
              <option value="all">All Items</option>
              <option value="conversation">Conversations</option>
              <option value="context">Context Updates</option>
            </select>
          </div>
        </div>
      </div>

      <div className="history-area">
        <div className="history-timeline">
          {Object.entries(groupedHistory).map(([dateGroup, items]) => (
            <div key={dateGroup} className="history-group">
              <div className="history-date-header">
                {dateGroup === 'current' ? 'This Month' : dateGroup}
              </div>
              {items.map(item => (
                <div key={item.id} className="history-item">
                  <div className="history-icon">
                    {getIcon(item.type)}
                  </div>
                  <div className="history-content">
                    <div className="history-text">{item.text}</div>
                    <div className="history-time">
                      {formatHistoryTime(item.timestamp)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ))}
          {filteredHistory.length === 0 && (
            <div className="no-results">
              No matching history items found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default History