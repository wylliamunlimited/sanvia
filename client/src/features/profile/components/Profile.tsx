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
    gender: userData.gender,
    sex: userData.sex,
    age: userData.age,
    conditions: userData.conditions,
    medications: userData.medications
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
      gender: userData.gender,
      sex: userData.sex,
      age: userData.age,
      conditions: userData.conditions,
      medications: userData.medications
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
      gender: userData.gender,
      sex: userData.sex,
      age: userData.age,
      conditions: userData.conditions,
      medications: userData.medications
    })
    setHasChanges(false)
  }

  const handleSave = async () => {
    try {
      await updateProfile(editedData)
      updateUserData(editedData)
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

      <h2 className="profile-subheader">Your profile</h2>

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
        
        <div className="section-divider"></div>
        
        <ConnectedAccounts />
      </div>
    </div>
  )
}

export default Profile 