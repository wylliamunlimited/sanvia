import { firestoreApi } from '../../../api/firestoreApi'

export const deleteUserData = async (): Promise<void> => {
  try {
    await firestoreApi.deleteUserData()
  } catch (error) {
    console.error('Error deleting user data:', error)
    throw error
  }
}

export const deleteAccount = async (): Promise<void> => {
  try {
    await firestoreApi.deleteAccount()
  } catch (error) {
    console.error('Error deleting account:', error)
    throw error
  }
}

export const deleteAllChats = async (): Promise<void> => {
  try {
    await firestoreApi.deleteAllChats()
  } catch (error) {
    console.error('Error deleting all chats:', error)
    throw error
  }
}

export const deleteAllDocuments = async (): Promise<void> => {
  try {
    await firestoreApi.deleteUserData() // This endpoint deletes all documents
  } catch (error) {
    console.error('Error deleting all documents:', error)
    throw error
  }
}
