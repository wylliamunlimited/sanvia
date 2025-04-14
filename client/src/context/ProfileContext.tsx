import React, { createContext, useState, useContext, ReactNode } from 'react';
import { firestoreApi } from '../api/firestoreApi';

interface ProfileData {
  firstName: string;
  lastName: string;
  height: string;
  weight: string;
  gender: string;
  sex: string;
  age: string;
  conditions: string[];
  medications: string[];
}

interface ProfileContextType {
  userData: ProfileData;
  setUserData: (data: ProfileData) => void;
  updateUserData: (data: ProfileData) => void;
}

// Create context with default values
const ProfileContext = createContext<ProfileContextType>({
  userData: {
    firstName: '',
    lastName: '',
    height: '',
    weight: '',
    gender: '',
    sex: '',
    age: '',
    conditions: [],
    medications: []
  },
  setUserData: () => {},
  updateUserData: () => {}
});

// Hook to use profile context
export const useProfile = () => useContext(ProfileContext);

// Provider component
export const ProfileProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [userData, setUserData] = useState<ProfileData>({
    firstName: '',
    lastName: '',
    height: '',
    weight: '',
    gender: '',
    sex: '',
    age: '',
    conditions: [],
    medications: []
  });

  const updateUserData = async (updatedData: ProfileData) => {
    try {
      // Update user data in Firestore
      await firestoreApi.uploadProfile(
        updatedData.age, updatedData.gender, updatedData.sex,
        updatedData.height, updatedData.weight, updatedData.conditions, updatedData.medications
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
        userData, 
        setUserData,
        updateUserData
      }}
    >
      {children}
    </ProfileContext.Provider>
  );
}; 