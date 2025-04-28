import React from 'react';
import './ProfileForm.css';
import { cmToFeetInches, feetInchesToCm, kgToLbs, lbsToKg } from '../utils/conversionUtils';
import { capitalizeFirstLetter } from '../../../shared/utils/capitalize';

interface ProfileData {
  firstName: string;
  lastName: string;
  height: string;
  weight: string;
  sex: string;
  age: string;
  conditions: string[];
}

interface ProfileFormProps {
  editedData: ProfileData;
  handleInputChange: (field: string, value: string) => void;
  heightUnit: string;
  weightUnit: string;
  setHeightUnit: (unit: string) => void;
  setWeightUnit: (unit: string) => void;
  hasChanges: boolean;
  handleSave: () => void;
  handleCancel: () => void;
}

const ProfileForm: React.FC<ProfileFormProps> = ({
  editedData,
  handleInputChange,
  heightUnit,
  weightUnit,
  setHeightUnit,
  setWeightUnit,
  hasChanges,
  handleSave,
  handleCancel
}) => {
  const handleHeightUnitChange = (newUnit: string) => {
    setHeightUnit(newUnit);
  };

  const handleWeightUnitChange = (newUnit: string) => {
    setWeightUnit(newUnit);
  };

  const renderHeightInput = () => {
    if (heightUnit === 'cm') {
      return (
        <input
          type="number"
          value={editedData.height || ''}
          onChange={(e) => {
            const value = e.target.value;
            if (value === '' || (Number(value) >= 0 && Number(value) <= 241)) {
              handleInputChange('height', value);
            }
          }}
          className="editable-input"
          min="0"
          max="241"
        />
      );
    }

    const { feet, inches } = cmToFeetInches(Number(editedData.height) || 0);
    
    return (
      <div className="feet-inches-inputs">
        <div className="feet-input">
          <input
            type="number"
            value={feet}
            onChange={(e) => {
              const newFeet = parseInt(e.target.value) || 0;
              if (newFeet >= 0 && newFeet <= 7) {
                handleInputChange('height', feetInchesToCm(newFeet, inches).toString());
              }
            }}
            className="editable-input"
            min="0"
            max="7"
          />
          <span className="unit-label">ft</span>
        </div>
        <div className="inches-input">
          <input
            type="number"
            value={inches}
            onChange={(e) => {
              const newInches = parseInt(e.target.value) || 0;
              if (newInches >= 0 && newInches < 12) {
                handleInputChange('height', feetInchesToCm(feet, newInches).toString());
              }
            }}
            className="editable-input"
            min="0"
            max="11"
          />
          <span className="unit-label">in</span>
        </div>
      </div>
    );
  };

  const renderWeightInput = () => {
    if (weightUnit === 'kg') {
      return (
        <input
          type="number"
          value={editedData.weight || ''}
          onChange={(e) => {
            const value = e.target.value;
            if (value === '' || (Number(value) >= 0 && Number(value) <= 454)) {
              handleInputChange('weight', value);
            }
          }}
          className="editable-input"
          min="0"
          max="454"
          step="0.1"
        />
      );
    }

    const weightInLbs = kgToLbs(Number(editedData.weight) || 0);
    
    return (
      <input
        type="number"
        value={weightInLbs}
        onChange={(e) => {
          const newLbs = parseInt(e.target.value) || 0;
          if (newLbs >= 0 && newLbs <= 1000) {
            handleInputChange('weight', lbsToKg(newLbs).toString());
          }
        }}
        className="editable-input"
        min="0"
        max="1000"
      />
    );
  };

  return (
    <>
      <div className="profile-fields">
        <div className="name-row">
          <div className="profile-field">
            <div className="field-label">First name</div>
            <input
              type="text"
              value={editedData.firstName}
              onChange={(e) => handleInputChange('firstName', capitalizeFirstLetter(e.target.value))}
              className="editable-input"
            />
          </div>
          
          <div className="profile-field">
            <div className="field-label">Last name</div>
            <input
              type="text"
              value={editedData.lastName}
              onChange={(e) => handleInputChange('lastName', capitalizeFirstLetter(e.target.value))}
              className="editable-input"
            />
          </div>
        </div>
        
        <div className="metrics-row">
          <div className="profile-field">
            <div className="field-label">Age</div>
            <input
              type="number"
              value={editedData.age}
              onChange={(e) => handleInputChange('age', e.target.value)}
              className="editable-input"
            />
          </div>
          
          <div className="profile-field">
            <div className="field-label">Sex</div>
            <select
              value={editedData.sex}
              onChange={(e) => handleInputChange('sex', e.target.value)}
              className="editable-input editable-select"
            >
              {!editedData.sex && <option value="">Select</option>}
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Intersex">Intersex</option>
            </select>
          </div>
        </div>
        
        <div className="metrics-row">
          <div className="profile-field">
            <div className="field-label">Height in 
              <select 
                value={heightUnit}
                onChange={(e) => handleHeightUnitChange(e.target.value)}
                className="unit-select"
              >
                <option value="cm">cm</option>
                <option value="ft-in">ft-in</option>
              </select>
            </div>
            {renderHeightInput()}
          </div>
          
          <div className="profile-field">
            <div className="field-label">Weight in
              <select 
                value={weightUnit}
                onChange={(e) => handleWeightUnitChange(e.target.value)}
                className="unit-select"
              >
                <option value="kg">kg</option>
                <option value="lb">lb</option>
              </select>
            </div>
            {renderWeightInput()}
          </div>
        </div>

        <div className="profile-field">
          <div className="field-label">Conditions</div>
            <input
              type="text"
              value={editedData.conditions}
              onChange={(e) => handleInputChange('conditions', capitalizeFirstLetter(e.target.value))}
              className="editable-input"
            />
          </div>
      </div>

      {hasChanges && (
        <div className="profile-action-buttons">
          <button onClick={handleSave} className="save-button">Update Profile</button>
          <span onClick={handleCancel} className="cancel-link">Cancel</span>
        </div>
      )}
    </>
  );
};

export default ProfileForm;