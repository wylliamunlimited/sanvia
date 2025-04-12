import React, { useState } from 'react';
import './ConnectedAccounts.css';
import { useAuth } from '../../../context/AuthContext';
import axios from 'axios';

const ConnectedAccounts: React.FC = () => {
  const { user } = useAuth();
  const [isConnecting, setIsConnecting] = useState(false);

  const handleHealthConnect = async () => {
    try {
      setIsConnecting(true);
      
      // Get the current token
      const token = await user?.getIdToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      const response = await axios.post('/api/healthconnect/connect', {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data.status === 'success') {
        // TODO: Show success message
        console.log('Health Connect connected successfully');
      }
    } catch (error) {
      console.error('Failed to connect Health Connect:', error);
      // TODO: Show error message
    } finally {
      setIsConnecting(false);
    }
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
          <button className="connect-button">Connect</button>
        </div>
        <div className="account-connection-item">
          <div className="service-info">
            <div className="service-logo health-connect-logo"></div>
            <span className="service-name">Health Connect</span>
          </div>
          <button 
            className="connect-button"
            onClick={handleHealthConnect}
            disabled={isConnecting}
          >
            {isConnecting ? 'Connecting...' : 'Connect'}
          </button>
        </div>
      </div>
    </>
  );
};

export default ConnectedAccounts;