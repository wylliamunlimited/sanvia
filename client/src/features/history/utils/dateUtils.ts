export type ChatSession = {
  id: string;
  title: string;
  timestamp: Date;
}

export const formatHistoryTime = (timestamp: Date) => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  const itemDate = new Date(timestamp.getFullYear(), timestamp.getMonth(), timestamp.getDate())
  const time = timestamp.toLocaleTimeString([], { 
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })

  if (itemDate.getTime() === today.getTime()) {
    return `Today at ${time}`
  } else if (itemDate.getTime() === yesterday.getTime()) {
    return `Yesterday at ${time}`
  } else {
    return `${timestamp.toLocaleDateString('en-US', { 
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })} at ${time}`
  }
}

export const groupSessionsByDate = (sessions: ChatSession[]) => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const oneWeekAgo = new Date(today)
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)

  const grouped = sessions.reduce((groups, session) => {
    const itemDate = new Date(session.timestamp.getFullYear(), session.timestamp.getMonth(), session.timestamp.getDate())
    
    let key
    if (itemDate.getTime() === today.getTime()) {
      key = 'Today'
    } else if (itemDate.getTime() === yesterday.getTime()) {
      key = 'Yesterday'
    } else if (session.timestamp.getTime() > oneWeekAgo.getTime()) {
      key = session.timestamp.toLocaleDateString('en-US', { 
        weekday: 'long'
      })
    } else {
      key = session.timestamp.toLocaleDateString('en-US', { 
        month: 'short',
        year: 'numeric'
      })
    }
    
    if (!groups[key]) {
      groups[key] = {
        timestamp: itemDate.getTime(),
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