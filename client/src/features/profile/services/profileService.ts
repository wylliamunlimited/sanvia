import { firestoreApi } from '../../../api/firestoreApi'

export interface ProfileUpdate {
  firstName: string
  lastName: string
  height: string
  weight: string
  gender: string
  sex: string
  age: string
  conditions: string[]
  medications: string[]
}

export const updateProfile = async (profile: ProfileUpdate): Promise<void> => {
  try {
    // Update profile data
    const response = await firestoreApi.updateProfile(
      profile.firstName,
      profile.lastName,
      profile.age,
      profile.gender,
      profile.sex,
      profile.height,
      profile.weight,
      profile.conditions,
      profile.medications
    )
    console.log('Update user information successful:', response)
  } catch (error) {
    console.error('Error updating profile:', error)
    throw error
  }
}