import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Survey.css';

const Survey = () => {
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [sex, setSex] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const handleNext = () => setStep(step + 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log({ age, gender, sex, height, weight });

    // Redirect to main page after completing the survey
    navigate('/');
  };

  return (
    <div className="survey-container">
      <h2 className="survey-title">Survey</h2>
      <form onSubmit={handleSubmit} className="survey-form">
        {step >= 1 && (
          <div className="survey-question">
            <label>Age:</label>
            <input
              type="number"
              min="1"
              max="120"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              required
            />
            {age && <button type="button" onClick={handleNext}>Next</button>}
          </div>
        )}

        {step >= 2 && (
          <div className="survey-question">
            <label>Gender:</label>
            <div className="options-container">
              <button 
                type="button" 
                className={gender === 'Men' ? 'selected' : ''}
                onClick={() => {
                  setGender('Men');
                  handleNext();
                }}>
                Men
              </button>
              <button 
                type="button" 
                className={gender === 'Women' ? 'selected' : ''}
                onClick={() => {
                  setGender('Women');
                  handleNext();
                }}>
                Women
              </button>
              <button 
                type="button" 
                className={gender === 'Nonbinary' ? 'selected' : ''}
                onClick={() => {
                  setGender('Nonbinary');
                  handleNext();
                }}>
                Other
              </button>
            </div>
          </div>
        )}

        {step >= 3 && (
          <div className="survey-question">
            <label>Sex:</label>
            <div className="options-container">
              <button 
                type="button" 
                className={sex === 'Male' ? 'selected' : ''}
                onClick={() => {
                  setSex('Male');
                  handleNext();
                }}>
                Male
              </button>
              <button 
                type="button" 
                className={sex === 'Female' ? 'selected' : ''}
                onClick={() => {
                  setSex('Female');
                  handleNext();
                }}>
                Female
              </button>
            </div>
            <input
              type="text"
              placeholder="Other (optional)"
              value={sex !== 'Male' && sex !== 'Female' ? sex : ''}
              onChange={(e) => setSex(e.target.value)}
            />
            {(sex || sex === '') && <button type="button" onClick={handleNext}>Next</button>}
          </div>
        )}

        {step >= 4 && (
          <div className="survey-question">
            <label>Height:</label>
            <input
              type="text"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              required
            />
            {height && <button type="button" onClick={handleNext}>Next</button>}
          </div>
        )}

        {step >= 5 && (
          <div className="survey-question">
            <label>Weight:</label>
            <input
              type="text"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              required
            />
            {weight && <button type="submit">Submit Survey</button>}
          </div>
        )}
      </form>
    </div>
  );
};

export default Survey;
