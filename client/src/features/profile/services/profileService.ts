import { firestoreApi } from '../../../api/firestoreApi'

export interface ProfileUpdate {
  firstName: string
  lastName: string
  height: string
  weight: string
  gender: string
  sex: string
  age: string
}

export const updateProfile = async (profile: ProfileUpdate): Promise<void> => {
  try {
    // Update profile metrics
    const profile_response = await firestoreApi.uploadProfile(
      profile.age,
      profile.gender,
      profile.sex,
      profile.height,
      profile.weight
    )
    console.log(`Uploading user profile (without names), result: ${profile_response}`)

    // Update user names
    const name_response = await firestoreApi.uploadNames(
      profile.firstName,
      profile.lastName
    )
    console.log(`Uploading user names, result: ${name_response}`)

    console.log('Update user information successful.')
  } catch (error) {
    console.error('Error updating profile:', error)
    throw error
  }
}