import chatApi from '../../../api/chatApi'

export interface ChatSession {
  id: string
  title: string
  timestamp: Date
}

export const fetchChatThreads = async (): Promise<ChatSession[]> => {
  try {
    const threads = await chatApi.getAllChatThreads()
    return threads.map(thread => {
      // Parse the date string in MM/DD/YY HH:MM:SS format
      const [datePart, timePart] = thread.last_updated_at.split(' ')
      const [month, day, year] = datePart.split('/')
      const [hours, minutes, seconds] = timePart.split(':')
      
      // Create date with 20xx year
      const fullYear = 2000 + parseInt(year)
      const timestamp = new Date(fullYear, parseInt(month) - 1, parseInt(day), 
                               parseInt(hours), parseInt(minutes), parseInt(seconds))
      
      return {
        id: thread.thread_id,
        title: thread.title || 'Untitled Chat',
        timestamp
      }
    })
  } catch (err) {
    console.error('Error fetching chat history:', err)
    throw new Error('Failed to load chat history.')
  }
}

export const deleteIndividualChat = async (chatId: string): Promise<void> => {
  try {
    await chatApi.deleteChatThread(chatId);
  } catch (error) {
    console.error('Error deleting chat:', error);
    throw error;
  }
};