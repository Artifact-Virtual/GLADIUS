import React from 'react';

const DatabaseConnectionStatus = ({ status = 'connected', latency = 45, lastUpdate = new Date() }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'connected': return '#4ade80';
      case 'connecting': return '#fbbf24';
      case 'disconnected': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'connected': return '✓';
      case 'connecting': return '⟳';
      case 'disconnected': return '✗';
      default: return '?';
    }
  };

  return (
    <div className="database-connection-status">
      <div className="status-header">
        <h3>Database Connection</h3>
        <div 
          className={`status-indicator ${status}`}
          style={{ backgroundColor: getStatusColor() }}
        >
          {getStatusIcon()}
        </div>
      </div>
      
      <div className="connection-details">
        <div className="detail-item">
          <span className="label">Status:</span>
          <span className={`value ${status}`}>{status.toUpperCase()}</span>
        </div>
        
        {status === 'connected' && (
          <>
            <div className="detail-item">
              <span className="label">Latency:</span>
              <span className="value">{latency}ms</span>
            </div>
            
            <div className="detail-item">
              <span className="label">Last Update:</span>
              <span className="value">{lastUpdate.toLocaleTimeString()}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DatabaseConnectionStatus;
