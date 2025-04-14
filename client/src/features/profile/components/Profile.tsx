import { useState, useEffect } from 'react'
import './Profile.css'
import { useProfile } from '../../../context/ProfileContext'
import Header from '../../../shared/components/Header'
import { getScrollbarWidth } from '../../../shared/utils/scrollbar'
import { updateProfile } from '../services/profileService'
import ProfileForm from './ProfileForm'
import ConnectedAccounts from './ConnectedAccounts'

const Profile = () => {
  const { userData, updateUserData } = useProfile()
  const [hasChanges, setHasChanges] = useState(false)

  // Form state
  const [editedData, setEditedData] = useState({
    firstName: userData.firstName,
    lastName: userData.lastName,
    height: userData.height,
    weight: userData.weight,
    sex: userData.sex,
    age: userData.age
  })
  const [heightUnit, setHeightUnit] = useState('cm')
  const [weightUnit, setWeightUnit] = useState('kg')

  // Set scrollbar width for consistent layout
  useEffect(() => {
    document.documentElement.style.setProperty('--scrollbar-width', `${getScrollbarWidth()}px`)
  }, [])

  // If userData changes, update form state
  useEffect(() => {
    setEditedData({
      firstName: userData.firstName,
      lastName: userData.lastName,
      height: userData.height,
      weight: userData.weight,
      sex: userData.sex,
      age: userData.age
    })
    setHasChanges(false)
  }, [userData])

  const handleInputChange = (field: string, value: string) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Check if any field has been changed
  useEffect(() => {
    const changed = Object.entries(editedData).some(
      ([key, value]) => value !== userData[key as keyof typeof userData]
    )
    setHasChanges(changed)
  }, [editedData, userData])

  const handleCancel = () => {
    setEditedData({
      firstName: userData.firstName,
      lastName: userData.lastName,
      height: userData.height,
      weight: userData.weight,
      sex: userData.sex,
      age: userData.age
    })
    setHasChanges(false)
  }

  const handleSave = async () => {
    const updatedProfile = {
      ...editedData,
      gender: userData.gender // Removing
    }

    try {
      await updateProfile(updatedProfile)
      updateUserData(updatedProfile)
      setHasChanges(false)
    } catch (e) {
      console.error('Failed to update profile:', e)
    }
  }

  return (
    <div className="profile-content">
      <Header 
        icon={<></>}
        title=""
      />

    <div className="profile-header">
        <Header 
          icon={
            <svg className="profile-logo" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            }
          title="Profile"
        />
      </div>
      <p className="profile-tag">Personal information</p>
      <div className="profile-area scrollable-area">
        <ProfileForm 
          editedData={editedData}
          handleInputChange={handleInputChange}
          heightUnit={heightUnit}
          weightUnit={weightUnit}
          setHeightUnit={setHeightUnit}
          setWeightUnit={setWeightUnit}
          hasChanges={hasChanges}
          handleSave={handleSave}
          handleCancel={handleCancel}
        />
      <p className="section-tag">Medication</p>
      <p className="section-tag">Diagnosis</p>
        
        
        <ConnectedAccounts />
      </div>
    </div>
  )
}

export default Profile 