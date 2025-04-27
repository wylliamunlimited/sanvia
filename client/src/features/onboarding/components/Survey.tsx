import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from "react-router-dom";
import "./Survey.css";
import { firestoreApi } from '../../../api/firestoreApi';
import { useProfile } from '../../../context/ProfileContext';

interface SurveyQuestion {
  id: string;
  text: string;
}



interface SurveyProps {
  onSurveyComplete: () => void;
}

const AnimatedSurvey: React.FC<SurveyProps> = ({ onSurveyComplete }) => {
  const { userData, setUserData } = useProfile();
  // Survey state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [previousQuestionIndex, setPreviousQuestionIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [transitionDirection, setTransitionDirection] = useState<'next' | 'prev'>('next');
  //medical serch
  const [allConditions, setAllConditions] = useState<string[]>([]);
  const [conditionsMap, setConditionsMap] = useState<Record<string, string>>({});
  const [isLoadingConditions, setIsLoadingConditions] = useState(false);
  const [conditionsError, setConditionsError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [filteredConditions, setFilteredConditions] = useState<string[]>([]);
  const [medicalConditions, setMedicalConditions] = useState<string[]>([]);
  const [medication, setMedication] = useState<string[]>([]);

    //meds
  const [medicationSearchTerm, setMedicationSearchTerm] = useState('');
  const [allMedications, setAllMedications] = useState<any[]>([]); // loaded from file 2
  const [filteredMedications, setFilteredMedications] = useState<any[]>([]);
  const [selectedMedication, setSelectedMedication] = useState<any | null>(null);
  const [strengthOptions, setStrengthOptions] = useState<string[]>([]);
  const [selectedStrength, setSelectedStrength] = useState('');
  const [isLoadingMedications, setIsLoadingMedications] = useState(false);
  const [medicationsError, setMedicationsError] = useState('');
  const [medicationsStrengthsMap, setMedicationsStrengthsMap] = useState<Record<string, string[]>>({});
  const [selectedMedications, setSelectedMedications] = useState<{medication: string, strength: string}[]>([]);
  const [prescribedMedications, setPrescribedMedications] = useState<string[]>([]);


  //MED JSON
  useEffect(() => {
    const fetchMedications = async () => {
      try {
        const response = await fetch('/drug-drugsfda-0001-of-0001.json');
        const data = await response.json();
  
        // Extract medication brand names
        const medications = data.results
          .filter((drug: { products?: { brand_name: string }[] }) => drug.products && drug.products.length > 0)
          .map((drug: { products: { brand_name: string }[] }) => 
            drug.products.map((product: { brand_name: string }) => product.brand_name)
          )
          .flat()
          .filter(Boolean); // remove null or undefined
  
        setAllMedications(medications);
      } catch (error) {
        console.error('Error loading medications:', error);
        setMedicationsError('Failed to load medications.');
      } finally {
        setIsLoadingMedications(false);
      }
    };
  
    fetchMedications();
  }, []);
  
  
  //medicine
  useEffect(() => {
    async function fetchMedications() {
      setIsLoadingMedications(true);
      try {
        const response = await fetch('/RxTermsArchive202504.txt');
        const textData = await response.text();
  
        // Split into lines
        const lines = textData.split('\n');
  
        // First line is headers
        const headers = lines[0].trim().split('|');
  
        // Parse the rest into objects
        const data = lines.slice(1).map((line) => {
          const values = line.trim().split('|');
          const entry: Record<string, string> = {};
          headers.forEach((header, index) => {
            entry[header] = values[index] || '';
          });
          return entry;
        });
  
        setAllMedications(data);
  
        const strengthsMap: Record<string, string[]> = {};
        data.forEach((med) => {
          const genericName = med['FULL_GENERIC_NAME'];
          const strength = med['STRENGTH'];
  
          if (genericName) {
            if (!strengthsMap[genericName]) {
              strengthsMap[genericName] = [];
            }
            if (strength && !strengthsMap[genericName].includes(strength)) {
              strengthsMap[genericName].push(strength);
            }
          }
        });
  
        setMedicationsStrengthsMap(strengthsMap);
      } catch (error) {
        console.error('Failed to fetch medications', error);
        setMedicationsError('Failed to load medications.');
      } finally {
        setIsLoadingMedications(false);
      }
    }
  
    fetchMedications();
  }, []);

  //medical info
  useEffect(() => {
    const fetchConditions = async () => {
      try {
        const response = await fetch('/consumer-conditions.json');
        const data = await response.json();
        
        //dropdwon suggestion
        const conditionNames = Object.keys(data); 
        setAllConditions(conditionNames);
        setConditionsMap(data); 
        setIsLoadingConditions(false);
      } catch (error) {
        console.error('Error loading conditions:', error);
        setConditionsError('Failed to load condition data.');
        setIsLoadingConditions(false);
      }
    };
  
    fetchConditions();
  }, []);
  


  // Form input states
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [sex, setSex] = useState('');
  const [height, setHeight] = useState('');
  const [feet, setFeet] = useState('');
  const [inches, setInches] = useState('');
  const [weight, setWeight] = useState('');
  const [heightUnit, setHeightUnit] = useState('cm');
  const [weightUnit, setWeightUnit] = useState('kg');


  // Define questions
  const questions: SurveyQuestion[] = [
    {
      id: 'age',
      text: "1. How old are you?",
    },
    {
      id: 'gender',
      text: "2. Select your gender:",
    },
    {
      id: 'sex',
      text: "3. Select your sex:",
    },
    {
      id: 'height',
      text: "4. What is your height?",
    },
    {
      id: 'weight',
      text: "5. What is your weight?",
    },
    {
      id: 'medicalConditions',
      text: "6. Select any medical conditions you have:",
    },
    {
      id: 'medication',
      text: "7. Select any medications thathave been prescribed:",
    }
  ];

  // Handle input validation
  const handleNumericInput = (setter: React.Dispatch<React.SetStateAction<string>>) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    // Only allow numbers 
    if (value === '' || /^[0-9]*\.?[0-9]*$/.test(value)) {
      setter(value);
    }
  };

  // Handle navigation to next question
  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setTransitionDirection('next');
      setPreviousQuestionIndex(currentQuestionIndex);
      setIsAnimating(true);
      setCurrentQuestionIndex(prevIndex => prevIndex + 1);

    } else {
      handleSubmit();
    }
  };

  // Handle navigation to previous question
  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setTransitionDirection('prev');
      setPreviousQuestionIndex(currentQuestionIndex);
      setIsAnimating(true);
      setCurrentQuestionIndex(prevIndex => prevIndex - 1);


    }
  };

  const handleSkip = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setTransitionDirection('next');
      setPreviousQuestionIndex(currentQuestionIndex);
      setIsAnimating(true);
      setCurrentQuestionIndex(prevIndex => prevIndex + 1);
    } else {
      handleSubmit();
    }
  };

  //unit conversion for height
  const toggleHeightUnit = () => {
    if (heightUnit === 'cm' && height) {
      // Convert cm to feet and inches
      const totalInches = parseFloat(height) / 2.54;
      const feetValue = Math.floor(totalInches / 12).toString();
      const inchesValue = Math.round(totalInches % 12).toString();
      setFeet(feetValue);
      setInches(inchesValue);
      setHeightUnit('ft');
    } else if (heightUnit === 'ft' && feet) {
      // Convert feet and inches to cm
      const totalInches = (parseFloat(feet) * 12) + (parseFloat(inches) || 0);
      const cmValue = Math.round(totalInches * 2.54).toString();
      setHeight(cmValue);
      setHeightUnit('cm');
    } else {
      setHeightUnit(heightUnit === 'cm' ? 'ft' : 'cm');
    }
  };

  // unit conversion for weight
  const toggleWeightUnit = () => {
    if (weightUnit === 'kg' && weight) {
      // Convert kg to lbs
      const lbsValue = (parseFloat(weight) * 2.20462).toFixed(1);
      setWeight(lbsValue);
      setWeightUnit('lbs');
    } else if (weightUnit === 'lbs' && weight) {
      // Convert lbs to kg
      const kgValue = (parseFloat(weight) / 2.20462).toFixed(1);
      setWeight(kgValue);
      setWeightUnit('kg');
    } else {
      setWeightUnit(weightUnit === 'kg' ? 'lbs' : 'kg');
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    setTransitionDirection('next');
    setPreviousQuestionIndex(currentQuestionIndex);
    setIsAnimating(true);
    setTimeout(() => {
      setIsCompleted(true);
      setIsAnimating(false);
    }, 500);

    const surveyData = {
      age,
      gender,
      sex,
      height: heightUnit === 'cm' ? height : `${feet}'${inches}"`,
      weight: `${weight}`,
      weightUnit: `${weightUnit}`,
      medicalConditions,
      medication
    };
    console.log('Survey submitted:', surveyData);

    // Upload to Firestore
    try {
      const response = await firestoreApi.updateProfile(
        userData.firstName,
        userData.lastName,
        age,
        gender,
        sex,
        height,
        weight,
        medicalConditions,
        []
      );
      console.log(`Uploaded survey data onto Firestore, ${response}`);

    } catch (err) {
      console.error('Survey Upload Failed. Error uploading data:', err)
    }
  };

  const handleRestart = () => {
    setAge('');
    setGender('');
    setSex('');
    setHeight('');
    setFeet('');
    setInches('');
    setWeight('');
    setHeightUnit('cm');
    setWeightUnit('kg');
    setMedicalConditions([]);
    setMedication([]);
    setIsCompleted(false);
    setPreviousQuestionIndex(0);
    setCurrentQuestionIndex(0);
    setTransitionDirection('prev');
  };
  
  const handleSurveyComplete = () => {
    onSurveyComplete();
    navigate("/");
  }

  // Check if current question can proceed
  const canProceed = () => {
    switch (currentQuestionIndex) {
      case 0: return !!age;
      case 1: return !!gender;
      case 2: return !!sex;
      case 3: return heightUnit === 'cm' ? !!height : (!!feet && !!inches);
      case 4: return !!weight;
      case 5: return true; 
      default: return false;
    }
  };
  
  const navigate = useNavigate();

  return (
    <div className="survey-container">
      {/* Background slides */}
      {/* Thank you background */}
      <div
        className="thank-you-background"
        style={{
          transform: `translateY(${isCompleted ? 0 : 100}vh)`,
        }}
      />
      {/* Survey content */}
      <div className="survey-content-container">
        {!isCompleted ? (
          <div
            className={`survey-form ${
              isAnimating
                ? transitionDirection === 'next'
                  ? 'animate-exit-up'
                  : 'animate-exit-down'
                : 'animate-enter'
            }`}
          >
            <div className="survey-card">
              <h2 className="question-title">
                {questions[currentQuestionIndex].text}
              </h2>

              {/* Question 1: Age */}
              {currentQuestionIndex === 0 && (
                <div className="question-container">
                  <input
                    type="number"
                    min="16"
                    max="100"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="Age (16-100)"
                    className="input-field"
                    required
                  />
                </div>
              )}

              {/* Question 2: Gender */}
              {currentQuestionIndex === 1 && (
                <div className="question-container">
                  <div className="option-grid">
                    {['Men', 'Women', 'Nonbinary'].map((option) => (
                      <button
                        key={option}
                        type="button"
                        className={`option-button ${gender === option ? 'selected' : ''}`}
                        onClick={() => setGender(option)}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Question 3: Sex */}
              {currentQuestionIndex === 2 && (
                <div className="question-container">
                  <div className="option-grid">
                    {['Male', 'Female', 'Intersex'].map((option) => (
                      <button
                        key={option}
                        type="button"
                        className={`option-button ${sex === option ? 'selected' : ''}`}
                        onClick={() => setSex(option)}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Question 4: Height */}
              {currentQuestionIndex === 3 && (
                <div className="question-container">

                  {heightUnit === 'cm' ? (
                    <input
                      type="text"
                      value={height}
                      onChange={handleNumericInput(setHeight)}
                      placeholder="Enter height in cm"
                      className="input-field"
                      required
                    />
                  ) : (
                    <div className="input-group">
                      <input
                        type="text"
                        value={feet}
                        onChange={handleNumericInput(setFeet)}
                        placeholder="Feet"
                        className="input-field half-width"
                        required
                      />
                      <input
                        type="text"
                        value={inches}
                        onChange={handleNumericInput(setInches)}
                        placeholder="Inches"
                        className="input-field half-width"
                        required
                      />
                    </div>
                  )}

                  <button
                    type="button"
                    onClick={toggleHeightUnit}
                    className="unit-toggle-button"
                  >
                    Convert to {heightUnit === 'cm' ? 'feet & inches' : 'cm'}
                  </button>
                </div>
              )}

              {/* Question 5: Weight */}
              {currentQuestionIndex === 4 && (
                <div className="question-container">
                  <input
                    type="text"
                    value={weight}
                    onChange={handleNumericInput(setWeight)}
                    placeholder={`Enter weight in ${weightUnit}`}
                    className="input-field"
                    required
                  />
                
                  <button
                    type="button"
                    onClick={toggleWeightUnit}
                    className="unit-toggle-button"
                  >
                    Convert to {weightUnit === 'kg' ? 'lbs' : 'kg'}
                  </button>
                </div>
              )}

              {/* Question 6: Medical Conditions */}
              {currentQuestionIndex === 5 && (
                <div className="question-container">
                  {/* search bar */}
                  <div className="search-container">
                    <input
                      type="text"
                      className="search-input-survey"
                      placeholder="Start typing a condition..."
                      value={searchTerm}
                      onChange={(e) => {
                        const value = e.target.value;
                        setSearchTerm(value);

                        //check that allConditions is an array before filtering
                        if (Array.isArray(allConditions)) {
                          const filtered = allConditions.filter((condition) =>
                            typeof condition === 'string' && 
                            condition.toLowerCase().includes(value.toLowerCase())
                          );
                          setFilteredConditions(filtered.slice(0, 10));
                        } else {
                          setFilteredConditions([]);
                          console.error('allConditions is not an array:', allConditions);
                        }
                      }}
                      disabled={medicalConditions.includes('None') || isLoadingConditions}
                    />

                    {isLoadingConditions && (
                      <div className="loading-indicator">Loading conditions...</div>
                    )}

                    {conditionsError && (
                      <div className="error-message">{conditionsError}</div>
                    )}

                    {/* results area */}
                    {searchTerm && filteredConditions.length > 0 && !isLoadingConditions && (
                      <ul className="search-results">
                        {filteredConditions.map((condition) => (
                          <li
                            key={condition}
                            className="search-result-item"
                            onClick={() => {
                              if (!medicalConditions.includes(condition)) {
                                setMedicalConditions((prev) => [...prev.filter(c => c !== 'None'), condition]);
                              }
                              setSearchTerm('');
                              setFilteredConditions([]);
                            }}
                            title={conditionsMap[condition] || 'No URL available'}
                          >
                            {condition}
                          </li>
                        ))}
                      </ul>
                    )}

                    {searchTerm && filteredConditions.length === 0 && !isLoadingConditions && (
                      <div className="no-results">No matching conditions found</div>
                    )}
                  </div>

                  {/* Show selected conditions as tags */}
                  <div className="tags-container">
                    {medicalConditions.length === 0 && (
                      /* declare no issues */
                      <button 
                        className="none-button"
                        onClick={() => setMedicalConditions(['None'])}
                      >
                        I have no medical conditions
                      </button>
                    )}
                    
                    {medicalConditions.map((condition) => (
                      <span
                        key={condition}
                        className="condition-tag"
                      >
                        {condition}
                        <button
                          className="tag-remove-button"
                          onClick={() => {
                            setMedicalConditions((prev) => prev.filter((c) => c !== condition));
                          }}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Question 7: Prescribed Medications */}
              {currentQuestionIndex === 6 && (
                <div className="question-container">
                  {/* search bar */}
                  <div className="search-container">
                    <input
                      type="text"
                      className="search-input-survey"
                      placeholder="Start typing a medication..."
                      value={medicationSearchTerm}
                      onChange={(e) => {
                        const value = e.target.value;
                        setMedicationSearchTerm(value);

                        // check that allMedications is an array before filtering
                        if (Array.isArray(allMedications)) {
                          const filtered = allMedications.filter((medication) =>
                            typeof medication === 'string' &&
                            medication.toLowerCase().includes(value.toLowerCase())
                          );
                          setFilteredMedications(filtered.slice(0, 10));
                        } else {
                          setFilteredMedications([]);
                          console.error('allMedications is not an array:', allMedications);
                        }
                      }}
                      disabled={prescribedMedications.includes('None') || isLoadingMedications}
                    />

                    {isLoadingMedications && (
                      <div className="loading-indicator">Loading medications...</div>
                    )}

                    {medicationsError && (
                      <div className="error-message">{medicationsError}</div>
                    )}

                    {/* results area */}
                    {medicationSearchTerm && filteredMedications.length > 0 && !isLoadingMedications && (
                      <ul className="search-results">
                        {filteredMedications.map((medication) => (
                          <li
                            key={medication}
                            className="search-result-item"
                            onClick={() => {
                              if (!prescribedMedications.includes(medication)) {
                                setPrescribedMedications((prev) => [...prev.filter(m => m !== 'None'), medication]);
                              }
                              setMedicationSearchTerm('');
                              setFilteredMedications([]);
                            }}
                          >
                            {medication}
                          </li>
                        ))}
                      </ul>
                    )}

                    {medicationSearchTerm && filteredMedications.length === 0 && !isLoadingMedications && (
                      <div className="no-results">No matching medications found</div>
                    )}
                  </div>

                  {/* Show selected medications as tags */}
                  <div className="tags-container">
                    {prescribedMedications.length === 0 && (
                      <button 
                        className="none-button"
                        onClick={() => setPrescribedMedications(['None'])}
                      >
                        I am not currently prescribed any medications
                      </button>
                    )}

                    {prescribedMedications.map((medication) => (
                      <span
                        key={medication}
                        className="condition-tag"
                      >
                        {medication}
                        <button
                          className="tag-remove-button"
                          onClick={() => {
                            setPrescribedMedications((prev) => prev.filter((m) => m !== medication));
                          }}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}



        
              {/* Question 7: Medication Name and Strength Selection */}
              {/* {currentQuestionIndex === 6 && (
                <div className="question-container">
                  {/* Medication Name Search Bar */}
                  {/* <div className="search-container">
                    <input
                      type="text"
                      className="search-input-survey"
                      placeholder="Start typing a medication..."
                      value={medicationSearchTerm}
                      onChange={(e) => {
                        const value = e.target.value;
                        setMedicationSearchTerm(value);

                        if (Array.isArray(allMedications)) {
                          const filtered = allMedications
                            .filter((med) =>
                              typeof med['DISPLAY_NAME'] === 'string' &&
                              med['DISPLAY_NAME'].toLowerCase().includes(value.toLowerCase())
                            )
                            .map((med) => med['DISPLAY_NAME']);

                          setFilteredMedications([...new Set(filtered)].slice(0, 10));
                        } else {
                          setFilteredMedications([]);
                          console.error('allMedications is not an array:', allMedications);
                        }
                      }}
                      disabled={selectedMedications.length > 0 || isLoadingMedications}
                    />

                    {isLoadingMedications && (
                      <div className="loading-indicator">Loading medications...</div>
                    )}

                    {medicationsError && (
                      <div className="error-message">{medicationsError}</div>
                    )}

                    {/* Search Results */}
                    {/* {medicationSearchTerm && filteredMedications.length > 0 && !isLoadingMedications && (
                      <ul className="search-results">
                        {filteredMedications.map((medName) => (
                          <li
                            key={medName}
                            className="search-result-item"
                            onClick={() => {
                              setSelectedMedication(medName);
                              setMedicationSearchTerm('');
                              setFilteredMedications([]);
                            }}
                          >
                            {medName}
                          </li>
                        ))}
                      </ul>
                    )}

                    {medicationSearchTerm && filteredMedications.length === 0 && !isLoadingMedications && (
                      <div className="no-results">No matching medications found</div>
                    )}
                  </div> */}

                  {/* Strength Picker (after medication is selected) */}
                  {/* {selectedMedication && (
                    <div className="strength-selection-container">
                      <h4 className="sub-question-title">Select strength for {selectedMedication}:</h4>

                      <div className="strength-buttons">
                        {(medicationsStrengthsMap[selectedMedication] || []).map((strength) => (
                          <button
                            key={strength}
                            className="strength-button"
                            onClick={() => {
                              setSelectedMedications((prev) => [
                                ...prev,
                                { medication: selectedMedication, strength }
                              ]);
                              setSelectedMedication(''); // Clear after selecting
                            }}
                          >
                            {strength}
                          </button>
                        ))}
                      </div>

                      {/* Option if no strength fits */}
                      {/* {(medicationsStrengthsMap[selectedMedication] || []).length === 0 && (
                        <p>No strengths available for this medication.</p>
                      )}
                    </div>
                  )}

                  {/* Show selected medications and strengths as tags */}
                  {/* <div className="tags-container">
                    {selectedMedications.map(({ medication, strength }) => (
                      <span key={`${medication}-${strength}`} className="condition-tag">
                        {medication} - {strength}
                        <button
                          className="tag-remove-button"
                          onClick={() => {
                            setSelectedMedications((prev) =>
                              prev.filter((item) => !(item.medication === medication && item.strength === strength))
                            );
                          }}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>  */
              // )} 
              }

        

              {/* Navigation buttons */}
              <div className="navigation-buttons">
                {currentQuestionIndex > 0 && (
                  <button
                    type="button"
                    onClick={handlePrevious}
                    className="back-button"
                  >
                    Back
                  </button>
                )}

                <button
                  type="button"
                  onClick={currentQuestionIndex === questions.length - 1 ? handleSubmit : handleNext}
                  disabled={!canProceed()}
                  className={`next-button ${!canProceed() ? 'disabled' : ''}`}
                >
                  {currentQuestionIndex === questions.length - 1 ? 'Submit' : 'Next'}
                </button>

                {currentQuestionIndex < questions.length - 1 && (
                  <button
                    type="button"
                    onClick={handleSkip}
                    className="skip-button"
                  >
                    Skip
                  </button>
                  )}
              </div>

              {/* Progress indicator */}
              <div className="progress-container">
                <div className="progress-text">
                  <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
                </div>
                <div className="progress-bar-container">
                  <div
                    className="progress-bar"
                    style={{ width: `${(currentQuestionIndex / (questions.length - 1)) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className={`summary-card ${isAnimating ? 'animate-exit-up' : 'animate-enter'}`}>
            <h2 className="summary-title">Thank you for completing the survey!</h2>
            <p className="summary-description">Your responses have been recorded.</p>

            <div className="summary-data">
              <h3 className="summary-subtitle">Survey Summary:</h3>
              <ul className="summary-list">
                <li><strong>Age:</strong> {age}</li>
                <li><strong>Gender:</strong> {gender}</li>
                <li><strong>Sex:</strong> {sex}</li>
                <li><strong>Height:</strong> {heightUnit === 'cm' ? `${height} cm` : `${feet}'${inches}"`}</li>
                <li><strong>Weight:</strong> {weight} {weightUnit}</li>
                <li><strong>Medical Conditions:</strong> {medicalConditions.length > 0 ? medicalConditions.join(', ') : 'None'}</li>
                <li><strong>Medication Prescription:</strong> {medicalConditions.length > 0 ? medicalConditions.join(', ') : 'None'}</li>

              </ul>
            </div>

            <div className="summary-buttons"> 
              <button
                onClick={handleRestart}
                className="summary-button"
              >
                Take Survey Again
              </button>
              <button
                onClick={handleSurveyComplete}
                className="summary-button"
              >
                Confirm
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnimatedSurvey;