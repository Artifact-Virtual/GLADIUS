import React, { useState, useEffect } from 'react';
import RealTimeAPIService from '../services/RealTimeAPIService';

/**
 * API Error Monitoring Component
 * Monitors API errors, response times, and failure patterns
 */
const ApiErrorMonitoring = () => {
  const [errorData, setErrorData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchErrorData = async () => {
      try {
        setIsLoading(true);
        const response = await RealTimeAPIService.makeRequest('/api/enterprise/api-errors');
        if (response) {
          setErrorData(response);
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('disconnected');
        }
        setLastUpdate(new Date().toISOString());
      } catch (error) {
        console.error('Failed to fetch error data:', error);
        setConnectionStatus('error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchErrorData();
    const interval = setInterval(fetchErrorData, 15000); // Update every 15 seconds
    
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="theme-card">
        <div className="theme-loading"></div>
        <p>Loading API error monitoring data...</p>
      </div>
    );
  }

  return (
    <div className="api-error-monitoring">
      <div className="theme-card">
        <h3>🚨 API Error Monitoring</h3>
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
        
        {errorData ? (
          <div className="error-data">
            <div className="theme-grid theme-grid-cols-4 theme-mb-lg">
              <div className="theme-metric-card">
                <div className="theme-metric-value theme-status-error">
                  {errorData.total_errors || 0}
                </div>
                <div className="theme-metric-label">Total Errors</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">
                  {errorData.error_rate || 0}%
                </div>
                <div className="theme-metric-label">Error Rate</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">
                  {errorData.avg_response_time || 0}ms
                </div>
                <div className="theme-metric-label">Avg Response</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">
                  {errorData.uptime || 0}%
                </div>
                <div className="theme-metric-label">Uptime</div>
              </div>
            </div>

            {errorData.recent_errors && errorData.recent_errors.length > 0 ? (
              <div className="recent-errors">
                <h4>Recent Errors</h4>
                <div className="error-list">
                  {errorData.recent_errors.slice(0, 10).map((error, index) => (
                    <div key={error.id || index} className="theme-alert-error">
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span><strong>{error.endpoint || 'Unknown endpoint'}</strong></span>
                        <span>{error.timestamp ? new Date(error.timestamp).toLocaleString() : 'Unknown time'}</span>
                      </div>
                      <div>Status: {error.status_code || 'Unknown'} - {error.message || 'No message'}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="theme-text-secondary">No recent errors</div>
            )}
          </div>
        ) : (
          <div className="theme-text-secondary">
            No error monitoring data available. Check API connectivity.
          </div>
        )}
      </div>
    </div>
  );
};

export default ApiErrorMonitoring;
