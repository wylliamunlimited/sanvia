import { firestoreApi } from '../../api/firestoreApi';
import './Profile.css';
import { useState } from 'react';

interface ProfileProps {
  firstName: string;
  lastName: string;
  height: string;
  weight: string;
  gender: string;
  sex: string;
  age: string;
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: {
    firstName: string;
    lastName: string;
    height: string;
    weight: string;
    gender: string;
    sex: string;
    age: string;
  }) => void;
}

const Profile: React.FC<ProfileProps> = ({
  firstName,
  lastName,
  height,
  weight,
  gender,
  sex,
  age,
  isOpen,
  onClose,
  onSave
}) => {
  console.log("Profile props:", { firstName, lastName, height, weight, gender, sex, age });
  const [isEditing, setIsEditing] = useState(false);

  //edited versions
  const [editedFirstName, setEditedFirstName] = useState(firstName);
  const [editedLastName, setEditedLastName] = useState(lastName);
  const [editedHeight, setEditedHeight] = useState(height);
  const [editedWeight, setEditedWeight] = useState(weight);
  const [editedGender, setEditedGender] = useState(gender);
  const [editedSex, setEditedSex] = useState(sex);
  const [editedAge, setEditedAge] = useState(age);


  const handleSave = async () => {
    const updatedProfile = {
      firstName: editedFirstName,
      lastName: editedLastName,
      height: editedHeight,
      weight: editedWeight,
      gender: editedGender,
      sex: editedSex,
      age: editedAge,
    };

    console.log('Updated profile:', updatedProfile);

    // Pass data to parent component
    try {
      const profile_response = await firestoreApi.uploadProfile(
        updatedProfile.age, updatedProfile.gender, updatedProfile.sex,
        updatedProfile.height, updatedProfile.weight
      );
      console.log(`Uploading user profile (without names), result: ${profile_response}`);

      const name_response = await firestoreApi.uploadNames(
        updatedProfile.firstName, updatedProfile.lastName
      );
      console.log(`Uploading user names, result: ${name_response}`);

      console.log(`Update user information successful.`);
    } catch (e) {
      console.log(`Error: ${e}`);
    }

    onSave(updatedProfile);
    setIsEditing(false);
  };
  console.log("Sidebar is rendering");
  
  if (!isOpen) return null;

  return (
    <div className="overlay" onClick={onClose}>
      <div className="card" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={onClose}
          className="close-button"
        >
          ✕
        </button>
        <div className="profile-card-icon">
          {firstName.charAt(0).toUpperCase()}
          {lastName.charAt(0).toUpperCase()}
        </div>

        <div className="profile-content">
          {/* editing the personal profile information */}
          {isEditing ? (
            <>
              <input
                type="text"
                value={editedFirstName}
                onChange={(e) => setEditedFirstName(e.target.value)}
              />
              <input
                type="text"
                value={editedLastName}
                onChange={(e) => setEditedLastName(e.target.value)}
              />
              <input
                type="number"
                placeholder='Age:'
                value={editedAge}
                onChange={(e) => setEditedAge(e.target.value)}
              />
              <input
                type="number"
                placeholder='Height:'
                value={editedHeight}
                onChange={(e) => setEditedHeight(e.target.value)}
              />
              <input
                type="number"
                placeholder='Weight:'
                value={editedWeight}
                onChange={(e) => setEditedWeight(e.target.value)}
              />
              <input
                type="text"
                placeholder='Gender:'
                value={editedGender}
                onChange={(e) => setEditedGender(e.target.value)}
              />
              <input
                type="text"
                value={editedSex}
                onChange={(e) => setEditedSex(e.target.value)}
              />
            </>
          ) : (
            <>

              <h2>{firstName} {lastName}</h2>
              <p><strong>Age:</strong> {age}</p>
              <p><strong>Height:</strong> {height}</p>
              <p><strong>Weight:</strong> {weight}</p>
              <p><strong>Gender:</strong> {gender}</p>
              <p><strong>Sex:</strong> {sex}</p>
            </>
          )}
        </div>
        <button
          onClick={isEditing ? handleSave : () => setIsEditing(true)}
          className="edit-button"
        >
          {isEditing ? 'Save' : 'Edit'}
        </button>
      </div>
    </div>
  );
};

export default Profile;
