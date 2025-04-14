import React from 'react';
import './ConnectedAccounts.css';
import whoopapi from '../../../api/external_auth';

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
          <button className="connect-button" onClick={whoopapi.connectWhoop}>Connect</button>
        </div>
        <div className="account-connection-item">
          <div className="service-info">
            <div className="service-logo samsung-health-logo"></div>
            <span className="service-name">Samsung Health</span>
          </div>
          <button className="connect-button">Connect</button>
        </div>
        <div className="account-connection-item">
          <div className="service-info">
            <div className="service-logo apple-health-logo"></div>
            <span className="service-name">Apple Health</span>
          </div>
          <button className="connect-button">Connect</button>
        </div>
      </div>
    </>
  );
};

export default ConnectedAccounts;