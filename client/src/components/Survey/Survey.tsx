import React, { useState, useEffect } from 'react';
import "./Survey.css";
interface SurveyQuestion {
  id: string;
  text: string;
  backgroundColor: string;
}

const AnimatedSurvey: React.FC = () => {
  // Survey state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [previousQuestionIndex, setPreviousQuestionIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [transitionDirection, setTransitionDirection] = useState<'next' | 'prev'>('next');

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
    }
  ];

  // Handle input validation
  const handleNumericInput = (setter: React.Dispatch<React.SetStateAction<string>>) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    // Only allow numbers and decimal point
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
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setIsAnimating(false);
      }, 500);
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
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex - 1);
        setIsAnimating(false);
      }, 500);
    }
  };

  // Toggle height unit and convert values
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
      // Just toggle the unit without conversion if no value entered
      setHeightUnit(heightUnit === 'cm' ? 'ft' : 'cm');
    }
  };

  // Toggle weight unit and convert values
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
      // Just toggle the unit without conversion if no value entered
      setWeightUnit(weightUnit === 'kg' ? 'lbs' : 'kg');
    }
  };

  // Handle form submission
  const handleSubmit = () => {
    setTransitionDirection('next');
    setPreviousQuestionIndex(currentQuestionIndex);
    setIsAnimating(true);
    setTimeout(() => {
      setIsCompleted(true);
      setIsAnimating(false);
    }, 500);

    // You could save the data here or send it to a server
    const surveyData = {
      age,
      gender,
      sex,
      height: heightUnit === 'cm' ? height : `${feet}'${inches}"`,
      weight: `${weight} ${weightUnit}`
    };
    console.log('Survey submitted:', surveyData);
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
    setIsCompleted(false);
    setPreviousQuestionIndex(0);
    setCurrentQuestionIndex(0);
    setTransitionDirection('prev');
  };

  // Check if current question can proceed
  const canProceed = () => {
    switch (currentQuestionIndex) {
      case 0: return !!age;
      case 1: return !!gender;
      case 2: return !!sex;
      case 3: return heightUnit === 'cm' ? !!height : (!!feet && !!inches);
      case 4: return !!weight;
      default: return false;
    }
  };

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden">
      {/* Animated background layers */}
      {questions.map((question, index) => {
      // Only render necessary backgrounds for performance
      if (index === currentQuestionIndex || index === previousQuestionIndex) {
        return (
          <div
            key={index}
            className="absolute inset-0 w-full h-full transition-all duration-700 ease-in-out"
            style={{
              transform: 
                transitionDirection === 'next' 
                  ? `translateY(${index < currentQuestionIndex ? '-100vh' : index > currentQuestionIndex ? '100vh' : '0'})`
                  : `translateY(${index > currentQuestionIndex ? '100vh' : index < currentQuestionIndex ? '-100vh' : '0'})`,
              backgroundColor: question.backgroundColor,
              zIndex: index === currentQuestionIndex ? 0 : -1,
              opacity: index === currentQuestionIndex ? 1 : 0.5
            }}
          />
        );
      }
      return null;
    })}

      {/* Thank you background */}
      <div 
        className="absolute inset-0 w-full h-full transition-all duration-700 ease-in-out"
        style={{ 
          transform: `translateY(${isCompleted ? 0 : 100}vh)`,
          backgroundColor: "#0047B3", // Deep royal blue for completion
          zIndex: isCompleted ? 0 : -1
        }}
      />

      {/* Survey content */}
      <div className="absolute inset-0 flex items-center justify-center px-4 z-10">
        {!isCompleted ? (
          <div 
            className={`w-full max-w-2xl transition-all duration-500 ${
              isAnimating 
                ? transitionDirection === 'next' 
                  ? 'opacity-0 transform -translate-y-12' 
                  : 'opacity-0 transform translate-y-12'
                : 'opacity-100 transform translate-y-0'
            }`}
          >
            <div className="bg-white bg-opacity-90 p-8 rounded-lg shadow-lg">
              <h2 className="text-3xl font-bold mb-8 text-gray-800">
                {questions[currentQuestionIndex].text}
              </h2>

              {/* Question 1: Age */}
              {currentQuestionIndex === 0 && (
                <div className="space-y-4">
                  <label className="block text-lg text-gray-700">Enter your age:</label>
                  <input
                    type="number"
                    min="16"
                    max="100"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="Age (16-100)"
                    className="w-full p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              )}

              {/* Question 2: Gender */}
              {currentQuestionIndex === 1 && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['Men', 'Women', 'Nonbinary'].map((option) => (
                      <button
                        key={option}
                        type="button"
                        className={`py-4 px-6 text-lg border border-gray-300 rounded-lg transition-all ${
                          gender === option
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'bg-white hover:bg-gray-50'
                        }`}
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
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['Male', 'Female', 'Intersex'].map((option) => (
                      <button
                        key={option}
                        type="button"
                        className={`py-4 px-6 text-lg border border-gray-300 rounded-lg transition-all ${
                          sex === option
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'bg-white hover:bg-gray-50'
                        }`}
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
                <div className="space-y-4">
                  <label className="block text-lg text-gray-700">Height ({heightUnit}):</label>
                  
                  {heightUnit === 'cm' ? (
                    <input
                      type="text"
                      value={height}
                      onChange={handleNumericInput(setHeight)}
                      placeholder="Enter height in cm"
                      className="w-full p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  ) : (
                    <div className="flex space-x-4">
                      <input
                        type="text"
                        value={feet}
                        onChange={handleNumericInput(setFeet)}
                        placeholder="Feet"
                        className="w-1/2 p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                      <input
                        type="text"
                        value={inches}
                        onChange={handleNumericInput(setInches)}
                        placeholder="Inches"
                        className="w-1/2 p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                  )}
                  
                  <button
                    type="button"
                    onClick={toggleHeightUnit}
                    className="mt-2 py-2 px-4 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                  >
                    Convert to {heightUnit === 'cm' ? 'feet & inches' : 'cm'}
                  </button>
                </div>
              )}

              {/* Question 5: Weight */}
              {currentQuestionIndex === 4 && (
                <div className="space-y-4">
                  <label className="block text-lg text-gray-700">Weight ({weightUnit}):</label>
                  <input
                    type="text"
                    value={weight}
                    onChange={handleNumericInput(setWeight)}
                    placeholder={`Enter weight in ${weightUnit}`}
                    className="w-full p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                  
                  <button
                    type="button"
                    onClick={toggleWeightUnit}
                    className="mt-2 py-2 px-4 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                  >
                    Convert to {weightUnit === 'kg' ? 'lbs' : 'kg'}
                  </button>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="mt-8 flex justify-end">
                {currentQuestionIndex > 0 && (
                  <button
                    type="button"
                    onClick={handlePrevious}
                    className="mr-4 py-3 px-6 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
                  >
                    Back
                  </button>
                )}
                
                <button
                  type="button"
                  onClick={currentQuestionIndex === questions.length - 1 ? handleSubmit : handleNext}
                  disabled={!canProceed()}
                  className={`py-3 px-6 rounded-lg transition ${
                    canProceed()
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {currentQuestionIndex === questions.length - 1 ? 'Submit' : 'Next'}
                </button>
              </div>

              {/* Progress indicator */}
              <div className="mt-8">
                <div className="flex justify-between text-sm text-gray-500">
                  <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
                  <span>{Math.round((currentQuestionIndex / (questions.length - 1)) * 100)}% complete</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden mt-2">
                  <div 
                    className="h-2 bg-blue-500 transition-all duration-700 ease-in-out" 
                    style={{ width: `${(currentQuestionIndex / (questions.length - 1)) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className={`text-center bg-white bg-opacity-90 p-8 rounded-lg shadow-xl transition-all duration-500 ${
            isAnimating ? 'opacity-0 transform translate-y-8' : 'opacity-100 transform translate-y-0'
          }`}>
            <h2 import React, { useState, useEffect } from 'react';
import "./Survey.css";
interface SurveyQuestion {
  id: string;
  text: string;
  backgroundColor: string;
}

const AnimatedSurvey: React.FC = () => {
  // Survey state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [previousQuestionIndex, setPreviousQuestionIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [transitionDirection, setTransitionDirection] = useState<'next' | 'prev'>('next');

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
    }
  ];

  // Handle input validation
  const handleNumericInput = (setter: React.Dispatch<React.SetStateAction<string>>) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    // Only allow numbers and decimal point
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
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setIsAnimating(false);
      }, 500);
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
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex - 1);
        setIsAnimating(false);
      }, 500);
    }
  };

  // Toggle height unit and convert values
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
      // Just toggle the unit without conversion if no value entered
      setHeightUnit(heightUnit === 'cm' ? 'ft' : 'cm');
    }
  };

  // Toggle weight unit and convert values
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
      // Just toggle the unit without conversion if no value entered
      setWeightUnit(weightUnit === 'kg' ? 'lbs' : 'kg');
    }
  };

  // Handle form submission
  const handleSubmit = () => {
    setTransitionDirection('next');
    setPreviousQuestionIndex(currentQuestionIndex);
    setIsAnimating(true);
    setTimeout(() => {
      setIsCompleted(true);
      setIsAnimating(false);
    }, 500);

    // You could save the data here or send it to a server
    const surveyData = {
      age,
      gender,
      sex,
      height: heightUnit === 'cm' ? height : `${feet}'${inches}"`,
      weight: `${weight} ${weightUnit}`
    };
    console.log('Survey submitted:', surveyData);
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
    setIsCompleted(false);
    setPreviousQuestionIndex(0);
    setCurrentQuestionIndex(0);
    setTransitionDirection('prev');
  };

  // Check if current question can proceed
  const canProceed = () => {
    switch (currentQuestionIndex) {
      case 0: return !!age;
      case 1: return !!gender;
      case 2: return !!sex;
      case 3: return heightUnit === 'cm' ? !!height : (!!feet && !!inches);
      case 4: return !!weight;
      default: return false;
    }
  };

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden">
      {/* Animated background layers */}
      {questions.map((question, index) => {
      // Only render necessary backgrounds for performance
      if (index === currentQuestionIndex || index === previousQuestionIndex) {
        return (
          <div
            key={index}
            className="absolute inset-0 w-full h-full transition-all duration-700 ease-in-out"
            style={{
              transform: 
                transitionDirection === 'next' 
                  ? `translateY(${index < currentQuestionIndex ? '-100vh' : index > currentQuestionIndex ? '100vh' : '0'})`
                  : `translateY(${index > currentQuestionIndex ? '100vh' : index < currentQuestionIndex ? '-100vh' : '0'})`,
              backgroundColor: question.backgroundColor,
              zIndex: index === currentQuestionIndex ? 0 : -1,
              opacity: index === currentQuestionIndex ? 1 : 0.5
            }}
          />
        );
      }
      return null;
    })}

      {/* Thank you background */}
      <div 
        className="absolute inset-0 w-full h-full transition-all duration-700 ease-in-out"
        style={{ 
          transform: `translateY(${isCompleted ? 0 : 100}vh)`,
          backgroundColor: "#0047B3", // Deep royal blue for completion
          zIndex: isCompleted ? 0 : -1
        }}
      />

      {/* Survey content */}
      <div className="absolute inset-0 flex items-center justify-center px-4 z-10">
        {!isCompleted ? (
          <div 
            className={`w-full max-w-2xl transition-all duration-500 ${
              isAnimating 
                ? transitionDirection === 'next' 
                  ? 'opacity-0 transform -translate-y-12' 
                  : 'opacity-0 transform translate-y-12'
                : 'opacity-100 transform translate-y-0'
            }`}
          >
            <div className="bg-white bg-opacity-90 p-8 rounded-lg shadow-lg">
              <h2 className="text-3xl font-bold mb-8 text-gray-800">
                {questions[currentQuestionIndex].text}
              </h2>

              {/* Question 1: Age */}
              {currentQuestionIndex === 0 && (
                <div className="space-y-4">
                  <label className="block text-lg text-gray-700">Enter your age:</label>
                  <input
                    type="number"
                    min="16"
                    max="100"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="Age (16-100)"
                    className="w-full p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              )}

              {/* Question 2: Gender */}
              {currentQuestionIndex === 1 && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['Men', 'Women', 'Nonbinary'].map((option) => (
                      <button
                        key={option}
                        type="button"
                        className={`py-4 px-6 text-lg border border-gray-300 rounded-lg transition-all ${
                          gender === option
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'bg-white hover:bg-gray-50'
                        }`}
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
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['Male', 'Female', 'Intersex'].map((option) => (
                      <button
                        key={option}
                        type="button"
                        className={`py-4 px-6 text-lg border border-gray-300 rounded-lg transition-all ${
                          sex === option
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'bg-white hover:bg-gray-50'
                        }`}
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
                <div className="space-y-4">
                  <label className="block text-lg text-gray-700">Height ({heightUnit}):</label>
                  
                  {heightUnit === 'cm' ? (
                    <input
                      type="text"
                      value={height}
                      onChange={handleNumericInput(setHeight)}
                      placeholder="Enter height in cm"
                      className="w-full p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  ) : (
                    <div className="flex space-x-4">
                      <input
                        type="text"
                        value={feet}
                        onChange={handleNumericInput(setFeet)}
                        placeholder="Feet"
                        className="w-1/2 p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                      <input
                        type="text"
                        value={inches}
                        onChange={handleNumericInput(setInches)}
                        placeholder="Inches"
                        className="w-1/2 p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                  )}
                  
                  <button
                    type="button"
                    onClick={toggleHeightUnit}
                    className="mt-2 py-2 px-4 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                  >
                    Convert to {heightUnit === 'cm' ? 'feet & inches' : 'cm'}
                  </button>
                </div>
              )}

              {/* Question 5: Weight */}
              {currentQuestionIndex === 4 && (
                <div className="space-y-4">
                  <label className="block text-lg text-gray-700">Weight ({weightUnit}):</label>
                  <input
                    type="text"
                    value={weight}
                    onChange={handleNumericInput(setWeight)}
                    placeholder={`Enter weight in ${weightUnit}`}
                    className="w-full p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                  
                  <button
                    type="button"
                    onClick={toggleWeightUnit}
                    className="mt-2 py-2 px-4 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                  >
                    Convert to {weightUnit === 'kg' ? 'lbs' : 'kg'}
                  </button>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="mt-8 flex justify-end">
                {currentQuestionIndex > 0 && (
                  <button
                    type="button"
                    onClick={handlePrevious}
                    className="mr-4 py-3 px-6 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
                  >
                    Back
                  </button>
                )}
                
                <button
                  type="button"
                  onClick={currentQuestionIndex === questions.length - 1 ? handleSubmit : handleNext}
                  disabled={!canProceed()}
                  className={`py-3 px-6 rounded-lg transition ${
                    canProceed()
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {currentQuestionIndex === questions.length - 1 ? 'Submit' : 'Next'}
                </button>
              </div>

              {/* Progress indicator */}
              <div className="mt-8">
                <div className="flex justify-between text-sm text-gray-500">
                  <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
                  <span>{Math.round((currentQuestionIndex / (questions.length - 1)) * 100)}% complete</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden mt-2">
                  <div 
                    className="h-2 bg-blue-500 transition-all duration-700 ease-in-out" 
                    style={{ width: `${(currentQuestionIndex / (questions.length - 1)) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className={`text-center bg-white bg-opacity-90 p-8 rounded-lg shadow-xl transition-all duration-500 ${
            isAnimating ? 'opacity-0 transform translate-y-8' : 'opacity-100 transform translate-y-0'
          }`}>
            <h2 className="text-3xl font-bold mb-4">Thank you for completing the survey!</h2>
            <p className="text-xl mb-6">Your responses have been recorded.</p>
            
            <div className="bg-gray-100 p-6 rounded-lg mb-6 text-left">
              <h3 className="text-xl font-semibold mb-4">Survey Summary:</h3>
              <ul className="space-y-2">
                <li><strong>Age:</strong> {age}</li>
                <li><strong>Gender:</strong> {gender}</li>
                <li><strong>Sex:</strong> {sex}</li>
                <li><strong>Height:</strong> {heightUnit === 'cm' ? `${height} cm` : `${feet}'${inches}"`}</li>
                <li><strong>Weight:</strong> {weight} {weightUnit}</li>
              </ul>
            </div>
            
            <button
              onClick={handleRestart}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition focus:outline-none focus:ring-2 focus:ring-blue-700"
            >
              Take Survey Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

function Survey() {
  return <AnimatedSurvey />;
}

export default Survey;
="text-3xl font-bold mb-4">Thank you for completing the survey!</h2>
            <p className="text-xl mb-6">Your responses have been recorded.</p>
            
            <div className="bg-gray-100 p-6 rounded-lg mb-6 text-left">
              <h3 className="text-xl font-semibold mb-4">Survey Summary:</h3>
              <ul className="space-y-2">
                <li><strong>Age:</strong> {age}</li>
                <li><strong>Gender:</strong> {gender}</li>
                <li><strong>Sex:</strong> {sex}</li>
                <li><strong>Height:</strong> {heightUnit === 'cm' ? `${height} cm` : `${feet}'${inches}"`}</li>
                <li><strong>Weight:</strong> {weight} {weightUnit}</li>
              </ul>
            </div>
            
            <button
              onClick={handleRestart}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition focus:outline-none focus:ring-2 focus:ring-blue-700"
            >
              Take Survey Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

function Survey() {
  return <AnimatedSurvey />;
}

export default Survey;
