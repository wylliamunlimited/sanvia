import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import "./Survey.css";
import { firestoreApi } from '../../../api/firestoreApi';
interface SurveyQuestion {
  id: string;
  text: string;
  backgroundColor: string;
}

interface SurveyProps {
  onSurveyComplete: () => void;
}

const AnimatedSurvey: React.FC<SurveyProps> = ({ onSurveyComplete }) => {
  // Survey state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [previousQuestionIndex, setPreviousQuestionIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [transitionDirection, setTransitionDirection] = useState<'next' | 'prev'>('next');
  const [activeIndices, setActiveIndices] = useState<number[]>([0]);
  //medical serch
  const [allConditions, setAllConditions] = useState<string[]>([]);
  const [conditionsMap, setConditionsMap] = useState<Record<string, string>>({});
  const [isLoadingConditions, setIsLoadingConditions] = useState(false);
  const [conditionsError, setConditionsError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [filteredConditions, setFilteredConditions] = useState<string[]>([]);
  const [medicalConditions, setMedicalConditions] = useState<string[]>([]);

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
      text: "How old are you?",
      backgroundColor: "#E6F2FF" // Very light blue
    },
    {
      id: 'gender',
      text: "Select your gender?",
      backgroundColor: "#B3D9FF" // Light blue
    },
    {
      id: 'sex',
      text: "Select your sex?",
      backgroundColor: "#80C1FF" // Medium blue
    },
    {
      id: 'height',
      text: "What is your height?",
      backgroundColor: "#4DA6FF" // Bright blue
    },
    {
      id: 'weight',
      text: "What is your weight?",
      backgroundColor: "#1A75FF" // Deep blue
    },
    {
      id: 'medicalConditions',
      text: "Select any medical conditions you have:",
      backgroundColor: "#0052cc" // Darker blue
    }
  ];

  // Keep track of active indices for animation
  useEffect(() => {
    setActiveIndices([previousQuestionIndex, currentQuestionIndex]);
  }, [currentQuestionIndex, previousQuestionIndex]);

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
      
      // Delay changing the current question to allow animation to start
      setTimeout(() => {
        setCurrentQuestionIndex(prevIndex => prevIndex + 1);
        setTimeout(() => {
          setIsAnimating(false);
        }, 50); // Small delay to ensure state is updated
      }, 50);
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
      
      // Delay changing the current question to allow animation to start
      setTimeout(() => {
        setCurrentQuestionIndex(prevIndex => prevIndex - 1);
        setTimeout(() => {
          setIsAnimating(false);
        }, 50); // Small delay to ensure state is updated
      }, 50);
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
      weight: `${weight}` ,
      weightUnit: `${weightUnit}`,
      medicalConditions
    };
    console.log('Survey submitted:', surveyData);

    // Upload to Firestore
    try {
      const response = await firestoreApi.uploadProfile(
        age, gender, sex, height, weight, medicalConditions, []
      )  // Change to chatApi.sendMessage once auth is implemented
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

  // Function to calculate the slide position based on direction and indices
  const getSlidePosition = (index: number) => {
    if (index === currentQuestionIndex) return 0;
    
    if (transitionDirection === 'next') {
      return index < currentQuestionIndex ? -100 : 100;
    } else {
      return index > currentQuestionIndex ? 100 : -100;
    }
  };

  return (
    <div className="survey-container">
      {/* Background slides */}
      {questions.map((question, index) => (
        <div
          key={index}
          className={`background-slide ${
            activeIndices.includes(index) ? 'active' : 'inactive'
          }`}
          style={{
            transform: `translateY(${activeIndices.includes(index) ? getSlidePosition(index) : index < currentQuestionIndex ? -100 : 100}vh)`,
            backgroundColor: question.backgroundColor,
            opacity: activeIndices.includes(index) ? 1 : 0
          }}
        />
      ))}

      {/* Thank you background */}
      <div
        className="thank-you-background"
        style={{
          transform: `translateY(${isCompleted ? 0 : 100}vh)`,
          backgroundColor: "#0047B3" // Deep royal blue for completion
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
                  <label className="input-label">Enter your age:</label>
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
                  <label className="input-label">Height ({heightUnit}):</label>

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
                  <label className="input-label">Weight ({weightUnit}):</label>
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
                  <label className="input-label">Search and select your conditions:</label>

                  {/* search bar */}
                  <div className="search-container">
                    <input
                      type="text"
                      className="search-input"
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