import { useState, useEffect } from 'react'
import './Profile.css'
import { useProfile } from '../../../context/ProfileContext'
import { getScrollbarWidth } from '../../../shared/utils/scrollbar'
import { updateProfile } from '../services/profileService'
import ProfileForm from './ProfileForm'
import ConnectedAccounts from './ConnectedAccounts'
import DangerZone from './DangerZone'
import { useLocation } from 'react-router-dom'

const Profile = () => {
  const { userData, updateUserData } = useProfile()
  const [hasChanges, setHasChanges] = useState(false)
  const location = useLocation()
  const [showSnackBar, setShowSnackBar] = useState(false)
  const [connectMessage, setConnectMessage] = useState("")

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

  // detect connection success
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get("connect-status") == "success") {
      
      setConnectMessage(`${params.get("provider")} successfully connected! We can now talk about your health based on ${params.get("provider")}.`)
      setShowSnackBar(true);
      window.history.replaceState({}, document.title, location.pathname);
      setTimeout(() => {
        setShowSnackBar(false);
      }, 4000);
    }
  }, [location]);

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

      {showSnackBar && (
        <div className="snackbar">
          ✅ {connectMessage}
          <button onClick={() => setShowSnackBar(false)} style={{ marginLeft: '12px', background: 'none', border: 'none', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}>
            ✕
          </button>
        </div>
      )}

      {showSnackBar && (
        <div className="snackbar">
          ✅ {connectMessage}
          <button onClick={() => setShowSnackBar(false)} style={{ marginLeft: '12px', background: 'none', border: 'none', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}>
            ✕
          </button>
        </div>
      )}

      {showSnackBar && (
        <div className="snackbar">
          ✅ {connectMessage}
          <button onClick={() => setShowSnackBar(false)} style={{ marginLeft: '12px', background: 'none', border: 'none', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}>
            ✕
          </button>
        </div>
      )}

      <div className="profile-area scrollable-area">
        <h2 className="profile-subheader">Your profile</h2>
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

        <div className="section-divider"></div>
        
        <DangerZone />
      </div>
    </div>
  )
}

export default Profile 