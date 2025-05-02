import { useNavigate } from 'react-router-dom';
import './Landing.css';

const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      <nav className="landing-nav">
        <div className="nav-left">
            <span className="landing-logo-text">Sanvia</span>
            <button className="nav-button about" onClick={() => navigate('/about')}> About </button>
        </div>
        <img src="./images/Vector.png"></img>
        <div className="nav-right">
          <button 
            className="nav-button login"
            onClick={() => navigate('/auth/login')}
          >
            Log In
          </button>
          <button 
            className="nav-button signup"
            onClick={() => navigate('/waitlist')}
          >
            Waitlist
          </button>
        </div>
      </nav>

      <main className="hero-section">
        <h1 className="hero-title">
          <span className="hero-text-bold">Secure&nbsp;</span>
          <span className="hero-text-regular"> Health.</span>
          <br />
          <span className="hero-text-bold">Secure</span>
          <span className="hero-text-regular"> Information.</span>
        </h1>
        
        <p className="hero-subtitle">
          Sanvia helps you make sense of your medical documents and health data
          <br />
          — with private, personalized answers you can trust.
        </p>

        <button 
          className="cta-button"
          onClick={() => navigate('/waitlist')}
        >
          Join the Waitlist
        </button>
      </main>
    </div>
  );
};

export default Landing; 