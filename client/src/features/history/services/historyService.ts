import chatApi from '../../../api/chatApi'

export interface ChatSession {
  id: string
  title: string
  timestamp: Date
}

export const fetchChatThreads = async (): Promise<ChatSession[]> => {
  try {
    const threads = await chatApi.getAllChatThreads()
    return threads.map(thread => ({
      id: thread.thread_id,
      title: thread.title || 'Untitled Chat',
      timestamp: new Date(thread.last_updated_at + 'Z'),
    }))
  } catch (err) {
    console.error('Error fetching chat history:', err)
    throw new Error('Failed to load chat history.')
  }
}