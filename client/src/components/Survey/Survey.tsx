import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Survey.css';

interface SurveyProps {
  onSurveyComplete: () => void;
}
const Survey: React.FC<SurveyProps> = ({ onSurveyComplete }) => {
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [sex, setSex] = useState('');
  const [height, setHeight] = useState('');
  const [feet, setFeet] = useState('');
  const [inches, setInches] = useState('');
  const [weight, setWeight] = useState('');
  const [heightUnit, setHeightUnit] = useState('cm'); // Default unit is cm
  const [weightUnit, setWeightUnit] = useState('kg'); // Default unit is kg
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const handleNext = () => setStep(step + 1);

  const handleSubmit = (e) => {
    e.preventDefault();
    const formattedHeight = heightUnit === 'cm' 
      ? `${height} cm` 
      : `${feet}'${inches}"`;

    console.log({ 
      age, 
      gender, 
      sex, 
      height: formattedHeight, 
      weight: `${weight} ${weightUnit}` 
    });

    // Redirect to main page after completing the survey
    onSurveyComplete();
    navigate('/');
  };

  const handleNumericInput = (setter) => (e) => {
    const value = e.target.value;
    if (value === '' || /^[0-9]*\.?[0-9]*$/.test(value)) {
      setter(value);
    }
  };

  const toggleHeightUnit = () => {
    if (heightUnit === 'cm') {
      // Convert cm to feet & inches
      const totalInches = parseFloat(height) / 2.54;
      const feetValue = Math.floor(totalInches / 12);
      const inchesValue = Math.round(totalInches % 12);
      
      setFeet(feetValue.toString());
      setInches(inchesValue.toString());
      setHeightUnit('feet');
    } else {
      // Convert feet & inches to cm
      const totalCm = (parseFloat(feet) * 12 + parseFloat(inches)) * 2.54;
      setHeight(totalCm.toFixed(2));
      setHeightUnit('cm');
    }
  };

  const toggleWeightUnit = () => {
    if (weight) {
      if (weightUnit === 'kg') {
        setWeight((parseFloat(weight) * 2.20462).toFixed(2)); // Convert kg to lbs
        setWeightUnit('lbs');
      } else {
        setWeight((parseFloat(weight) / 2.20462).toFixed(2)); // Convert lbs to kg
        setWeightUnit('kg');
      }
    }
  };

  return (
    <div className="survey-container">
      <h1 className="survey-title">Survey</h1>
      <form onSubmit={handleSubmit} className="survey-form">
        {step >= 1 && (
          <div className="survey-question">
            <label>Age:</label>
            <input
              type="number"
              min="16"
              max="100"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter your age:"
              required
            />
            {age && <button type="button" onClick={handleNext}>Next</button>}
          </div>
        )}

        {step >= 2 && (
          <div className="survey-question">
            <label>Gender:</label>
            <div className="options-container">
              {['Men', 'Women', 'Nonbinary'].map((option) => (
                <button 
                  key={option}
                  type="button"
                  className={gender === option ? 'selected' : ''}
                  onClick={() => { setGender(option); handleNext(); }}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        )}

        {step >= 3 && (
          <div className="survey-question">
            <label>Sex:</label>
            <div className="options-container">
              {['Male', 'Female', 'Intersex'].map((option) => (
                <button 
                  key={option}
                  type="button"
                  className={sex === option ? 'selected' : ''}
                  onClick={() => { setSex(option); handleNext(); }}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        )}

        {step >= 4 && (
          <div className="survey-question">
            <label>Height ({heightUnit}):</label>
            {heightUnit === 'cm' ? (
              <input
                type="text"
                value={height}
                placeholder="Enter height in cm"
                onChange={handleNumericInput(setHeight)}
                required
              />
            ) : (
              <div className="height-input">
                <input
                  type="text"
                  value={feet}
                  placeholder="Feet"
                  onChange={handleNumericInput(setFeet)}
                  required
                />
                <input
                  type="text"
                  value={inches}
                  placeholder="Inches"
                  onChange={handleNumericInput(setInches)}
                  required
                />
              </div>
            )}
            <button type="button" onClick={toggleHeightUnit}>
              Convert to {heightUnit === 'cm' ? 'feet & inches' : 'cm'}
            </button>
            {(height || feet) && <button type="button" onClick={handleNext}>Next</button>}
          </div>
        )}

        {step >= 5 && (
          <div className="survey-question">
            <label>Weight ({weightUnit}):</label>
            <input
              type="text"
              value={weight}
              placeholder={`Enter weight in ${weightUnit}`}
              onChange={handleNumericInput(setWeight)}
              required
            />
            <button type="button" onClick={toggleWeightUnit}>
              Convert to {weightUnit === 'kg' ? 'lbs' : 'kg'}
            </button>
            {weight && <button type="submit">Submit Survey</button>}
          </div>
        )}
      </form>
    </div>
  );
};

export default Survey;
