import React, { createContext, useState, useContext, ReactNode } from 'react';
import { firestoreApi } from '../api/firestoreApi';
import Profile from '../features/profile/components/Profile';

interface ProfileData {
  firstName: string;
  lastName: string;
  height: string;
  weight: string;
  gender: string;
  sex: string;
  age: string;
}

interface ProfileContextType {
  showProfile: boolean;
  openProfile: () => void;
  closeProfile: () => void;
  userData: ProfileData;
  setUserData: (data: ProfileData) => void;
  updateUserData: (data: ProfileData) => void;
}

// Create context with default values
const ProfileContext = createContext<ProfileContextType>({
  showProfile: false,
  openProfile: () => {},
  closeProfile: () => {},
  userData: {
    firstName: '',
    lastName: '',
    height: '',
    weight: '',
    gender: '',
    sex: '',
    age: ''
  },
  setUserData: () => {},
  updateUserData: () => {}
});

// Hook to use profile context
export const useProfile = () => useContext(ProfileContext);

// Provider component
export const ProfileProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [showProfile, setShowProfile] = useState(false);
  const [userData, setUserData] = useState<ProfileData>({
    firstName: '',
    lastName: '',
    height: '',
    weight: '',
    gender: '',
    sex: '',
    age: ''
  });

  const openProfile = () => {
    setShowProfile(true);
  };

  const closeProfile = () => {
    setShowProfile(false);
  };

  const updateUserData = async (updatedData: ProfileData) => {
    try {
      // Update user data in Firestore
      await firestoreApi.uploadProfile(
        updatedData.age, updatedData.gender, updatedData.sex,
        updatedData.height, updatedData.weight
      );
      await firestoreApi.uploadNames(
        updatedData.firstName, updatedData.lastName
      );
      
      // Update local state
      setUserData(updatedData);
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  return (
    <ProfileContext.Provider 
      value={{ 
        showProfile, 
        openProfile, 
        closeProfile, 
        userData, 
        setUserData,
        updateUserData
      }}
    >
      {children}
      <Profile 
        {...userData} 
        isOpen={showProfile} 
        onClose={closeProfile} 
        onSave={updateUserData}
      />
    </ProfileContext.Provider>
  );
}; 