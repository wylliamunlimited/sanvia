import React from 'react';
import './ConnectedAccounts.css';
import { whoopapi, epicapi } from '../../../api/external_auth';

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
            <div className="service-logo epic-logo"></div>
            <span className="service-name">EPIC</span>
          </div>
          <button className="connect-button" onClick={() => {
            const providerUrl = "https://fhir.epic.com/interconnect-fhir-oauth/";
            epicapi.connectEpic(providerUrl) // default: test server
          }}>Connect</button>
        </div>
      </div>
    </>
  );
};

export default ConnectedAccounts;