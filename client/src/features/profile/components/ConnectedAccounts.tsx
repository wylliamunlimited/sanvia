import React, { useState } from 'react';
import './ConnectedAccounts.css';
import { whoopapi, epicapi } from '../../../api/external_auth';
import EpicOrganizationSelector from './EpicOrganizationSelector';

const ConnectedAccounts: React.FC = () => {
  const [showEpicSelector, setShowEpicSelector] = useState(false);

  const handleEpicSelect = (endpoint: string) => {
    setShowEpicSelector(false);
    epicapi.connectEpic(endpoint);
  };

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
            <div className="service-logo epic-logo"></div>
            <span className="service-name">EPIC</span>
          </div>
          <div style={{ position: 'relative' }}>
            <button 
              className="connect-button" 
              onClick={() => setShowEpicSelector(true)}
            >
              Connect
            </button>
            {showEpicSelector && (
              <EpicOrganizationSelector
                onSelect={handleEpicSelect}
                onClose={() => setShowEpicSelector(false)}
              />
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default ConnectedAccounts;