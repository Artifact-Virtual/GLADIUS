import React, { useState, useEffect } from 'react';
import RealTimeAPIService from '../services/RealTimeAPIService';

/**
 * API Integration Tools Component
 * Manages API connections, testing, and configuration
 */
const ApiIntegrationTools = () => {
  const [integrationData, setIntegrationData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchIntegrationData = async () => {
      try {
        setIsLoading(true);
        const response = await RealTimeAPIService.makeRequest('/api/enterprise/api-integrations');
        if (response) {
          setIntegrationData(response);
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('disconnected');
        }
        setLastUpdate(new Date().toISOString());
      } catch (error) {
        console.error('Failed to fetch integration data:', error);
        setConnectionStatus('error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchIntegrationData();
    const interval = setInterval(fetchIntegrationData, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="theme-card">
        <div className="theme-loading"></div>
        <p>Loading API integration data...</p>
      </div>
    );
  }

  return (
    <div className="api-integration-tools">
      <div className="theme-card">
        <h3>🔗 API Integration Tools</h3>
        <div className="connection-status">
          Status: <span className={`theme-status-${connectionStatus === 'connected' ? 'operational' : 'error'}`}>
            {connectionStatus}
          </span>
          {lastUpdate && (
            <span style={{ marginLeft: '10px', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              Last updated: {new Date(lastUpdate).toLocaleTimeString()}
            </span>
          )}
        </div>
        
        {integrationData ? (
          <div className="integration-data">
            {integrationData.apis && integrationData.apis.length > 0 ? (
              <div className="theme-grid theme-grid-cols-2">
                {integrationData.apis.map((api, index) => (
                  <div key={api.id || index} className="theme-card">
                    <h4>{api.name || `API ${index + 1}`}</h4>
                    <div>Status: <span className={`theme-status-${api.status === 'active' ? 'operational' : 'error'}`}>
                      {api.status || 'unknown'}
                    </span></div>
                    <div>Endpoint: {api.endpoint || 'N/A'}</div>
                    <div>Last Response: {api.last_response_time || 'N/A'}ms</div>
                    <div>Success Rate: {api.success_rate || 0}%</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="theme-text-secondary">No API integration data available</div>
            )}
          </div>
        ) : (
          <div className="theme-text-secondary">
            No integration data available. Check API connectivity.
          </div>
        )}
      </div>
    </div>
  );
};

export default ApiIntegrationTools;
