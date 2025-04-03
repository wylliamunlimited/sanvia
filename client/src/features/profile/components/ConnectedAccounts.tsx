import React from 'react';
import './ConnectedAccounts.css';

const ConnectedAccounts: React.FC = () => {
  return (
    <>
      <h3 className="connected-accounts-header">Connected accounts</h3>
      <p className="connected-accounts-description">
        Connect Sanvia to other apps and services to sync your health data.
      </p>
      <div className="connected-accounts">
        <div className="account-connection-item">
          <div className="service-info">
            <div className="service-logo whoop-logo"></div>
            <span className="service-name">WHOOP</span>
          </div>
          <button className="connect-button">Connect</button>
        </div>
      </div>
    </>
  );
};

export default ConnectedAccounts;