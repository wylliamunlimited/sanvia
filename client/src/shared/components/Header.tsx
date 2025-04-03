import React from 'react';
import './Header.css';

interface HeaderProps {
  icon: React.ReactNode;
  title: string;
}

const Header: React.FC<HeaderProps> = ({ icon, title }) => {
  return (
    <div className="header">
      <div className="header-content">
        {icon}
        <h2>{title}</h2>
      </div>
    </div>
  );
};

export default Header; 