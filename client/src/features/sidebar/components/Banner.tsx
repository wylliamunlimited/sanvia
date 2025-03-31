import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Banner.css';

type BannerProps = {
  isVisible: boolean;
};

const Banner: React.FC<BannerProps> = ({ isVisible }) => {
  const navigate = useNavigate();
  
  if (!isVisible) return null;
  
  return (
    <div className="banner">
      <p>Personalize your Sanvia experience!</p>
      <button onClick={() => navigate("/onboarding")}>
        Complete Profile
      </button>
    </div>
  );
};

export default Banner; 