import React, { useState, useEffect } from 'react';

/**
 * SystemAlertsPanel - Real-time system alerts and notifications management
 * 
 * Displays critical system alerts, warnings, and informational messages
 * with priority-based filtering and emergency escalation capabilities.
 */
const SystemAlertsPanel = ({ 
  alerts = [], 
  emergencyMode = false, 
  onAlertAction = () => {} 
}) => {
  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [filterSeverity, setFilterSeverity] = useState('all'); // 'all', 'critical', 'warning', 'info'
  const [filterCategory, setFilterCategory] = useState('all'); // 'all', 'system', 'agent', 'workflow', 'api'
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState(new Set());
  const [mutedAlerts, setMutedAlerts] = useState(new Set());
  const [sortBy, setSortBy] = useState('timestamp'); // 'timestamp', 'severity', 'category'

  // Filter and sort alerts
  useEffect(() => {
    let filtered = alerts.filter(alert => {
      // Filter by severity
      if (filterSeverity !== 'all' && alert.severity !== filterSeverity) {
        return false;
      }
      
      // Filter by category
      if (filterCategory !== 'all' && alert.category !== filterCategory) {
        return false;
      }
      
      // Hide muted alerts unless in emergency mode
      if (!emergencyMode && mutedAlerts.has(alert.id)) {
        return false;
      }
      
      return true;
    });

    // Sort alerts
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'severity':
          const severityOrder = { critical: 3, warning: 2, info: 1 };
          return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
        case 'category':
          return a.category.localeCompare(b.category);
        case 'timestamp':
        default:
          return new Date(b.timestamp) - new Date(a.timestamp);
      }
    });

    setFilteredAlerts(filtered);
  }, [alerts, filterSeverity, filterCategory, mutedAlerts, emergencyMode, sortBy]);

  // Get alert severity information
  const getAlertSeverityInfo = (severity) => {
    switch (severity) {
      case 'critical':
        return {
          color: 'critical',
          icon: '🚨',
          bgColor: 'rgba(220, 53, 69, 0.1)',
          borderColor: '#dc3545'
        };
      case 'warning':
        return {
          color: 'warning',
          icon: '⚠️',
          bgColor: 'rgba(255, 193, 7, 0.1)',
          borderColor: '#ffc107'
        };
      case 'info':
        return {
          color: 'info',
          icon: 'ℹ️',
          bgColor: 'rgba(23, 162, 184, 0.1)',
          borderColor: '#17a2b8'
        };
      default:
        return {
          color: 'unknown',
          icon: '❓',
          bgColor: 'rgba(108, 117, 125, 0.1)',
          borderColor: '#6c757d'
        };
    }
  };

  // Get alert category icon
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'system': return '🖥️';
      case 'agent': return '🤖';
      case 'workflow': return '⚡';
      case 'api': return '🌐';
      case 'database': return '🗄️';
      case 'security': return '🔒';
      default: return '📋';
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / 60000);
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  // Handle alert actions
  const handleAcknowledge = (alertId) => {
    setAcknowledgedAlerts(prev => new Set([...prev, alertId]));
    onAlertAction(alertId, 'acknowledge');
  };

  const handleMute = (alertId) => {
    setMutedAlerts(prev => new Set([...prev, alertId]));
    onAlertAction(alertId, 'mute');
  };

  const handleDismiss = (alertId) => {
    onAlertAction(alertId, 'dismiss');
  };

  const handleEscalate = (alertId) => {
    onAlertAction(alertId, 'escalate');
  };

  // Calculate alert statistics
  const alertStats = {
    total: alerts.length,
    critical: alerts.filter(a => a.severity === 'critical').length,
    warning: alerts.filter(a => a.severity === 'warning').length,
    info: alerts.filter(a => a.severity === 'info').length,
    acknowledged: acknowledgedAlerts.size,
    muted: mutedAlerts.size
  };

  return (
    <div className={`system-alerts-panel ${emergencyMode ? 'emergency' : ''}`}>
      <div className="alerts-header">
        <div className="header-left">
          <h3 className="alerts-title">
            <span className="title-icon">🚨</span>
            System Alerts
          </h3>
          <div className="alert-stats">
            <div className="stat-item total">
              <span className="stat-value">{alertStats.total}</span>
              <span className="stat-label">Total</span>
            </div>
            <div className="stat-item critical">
              <span className="stat-value">{alertStats.critical}</span>
              <span className="stat-label">Critical</span>
            </div>
            <div className="stat-item warning">
              <span className="stat-value">{alertStats.warning}</span>
              <span className="stat-label">Warning</span>
            </div>
            <div className="stat-item info">
              <span className="stat-value">{alertStats.info}</span>
              <span className="stat-label">Info</span>
            </div>
          </div>
        </div>

        <div className="header-controls">
          <div className="filter-row">
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="filter-select severity-filter"
            >
              <option value="all">All Severity</option>
              <option value="critical">Critical ({alertStats.critical})</option>
              <option value="warning">Warning ({alertStats.warning})</option>
              <option value="info">Info ({alertStats.info})</option>
            </select>

            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="filter-select category-filter"
            >
              <option value="all">All Categories</option>
              <option value="system">System</option>
              <option value="agent">Agent</option>
              <option value="workflow">Workflow</option>
              <option value="api">API</option>
              <option value="database">Database</option>
              <option value="security">Security</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="filter-select sort-filter"
            >
              <option value="timestamp">Sort by Time</option>
              <option value="severity">Sort by Severity</option>
              <option value="category">Sort by Category</option>
            </select>
          </div>

          <div className="action-row">
            <button 
              className="bulk-action-btn acknowledge-all"
              onClick={() => {
                filteredAlerts.forEach(alert => {
                  if (!acknowledgedAlerts.has(alert.id)) {
                    handleAcknowledge(alert.id);
                  }
                });
              }}
              disabled={filteredAlerts.length === 0}
            >
              ✓ Acknowledge All
            </button>
            
            <button 
              className="bulk-action-btn clear-acknowledged"
              onClick={() => setAcknowledgedAlerts(new Set())}
              disabled={acknowledgedAlerts.size === 0}
            >
              🗑️ Clear Acknowledged
            </button>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="alerts-container">
        {filteredAlerts.length === 0 ? (
          <div className="empty-alerts">
            <span className="empty-icon">✅</span>
            <h4>No Active Alerts</h4>
            <p>All systems are operating normally.</p>
          </div>
        ) : (
          <div className="alerts-list">
            {filteredAlerts.map((alert) => {
              const severityInfo = getAlertSeverityInfo(alert.severity);
              const isAcknowledged = acknowledgedAlerts.has(alert.id);
              const isMuted = mutedAlerts.has(alert.id);
              
              return (
                <div
                  key={alert.id}
                  className={`alert-item ${severityInfo.color} ${isAcknowledged ? 'acknowledged' : ''} ${isMuted ? 'muted' : ''}`}
                  style={{ 
                    background: severityInfo.bgColor,
                    borderLeftColor: severityInfo.borderColor 
                  }}
                >
                  <div className="alert-main">
                    <div className="alert-header">
                      <div className="alert-indicators">
                        <span className="severity-icon">{severityInfo.icon}</span>
                        <span className="category-icon">{getCategoryIcon(alert.category)}</span>
                      </div>
                      
                      <div className="alert-metadata">
                        <span className={`severity-badge ${severityInfo.color}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="category-badge">
                          {alert.category.toUpperCase()}
                        </span>
                        <span className="timestamp">
                          {formatTimestamp(alert.timestamp)}
                        </span>
                      </div>

                      <div className="alert-status">
                        {isAcknowledged && <span className="status-badge acknowledged">✓ ACK</span>}
                        {isMuted && <span className="status-badge muted">🔇 MUTED</span>}
                        {emergencyMode && alert.severity === 'critical' && (
                          <span className="status-badge emergency">🚨 EMERGENCY</span>
                        )}
                      </div>
                    </div>

                    <div className="alert-content">
                      <h4 className="alert-title">{alert.title}</h4>
                      <p className="alert-message">{alert.message}</p>
                      
                      {alert.details && (
                        <div className="alert-details">
                          <div className="details-grid">
                            {Object.entries(alert.details).map(([key, value]) => (
                              <div key={key} className="detail-item">
                                <span className="detail-key">{key}:</span>
                                <span className="detail-value">{value}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {alert.source && (
                        <div className="alert-source">
                          <span className="source-label">Source:</span>
                          <span className="source-value">{alert.source}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="alert-actions">
                    {!isAcknowledged && (
                      <button
                        className="alert-action-btn acknowledge"
                        onClick={() => handleAcknowledge(alert.id)}
                        title="Acknowledge Alert"
                      >
                        ✓
                      </button>
                    )}
                    
                    {!isMuted && (
                      <button
                        className="alert-action-btn mute"
                        onClick={() => handleMute(alert.id)}
                        title="Mute Alert"
                      >
                        🔇
                      </button>
                    )}
                    
                    {alert.severity === 'critical' && emergencyMode && (
                      <button
                        className="alert-action-btn escalate"
                        onClick={() => handleEscalate(alert.id)}
                        title="Escalate Alert"
                      >
                        ⚠️
                      </button>
                    )}
                    
                    <button
                      className="alert-action-btn dismiss"
                      onClick={() => handleDismiss(alert.id)}
                      title="Dismiss Alert"
                    >
                      ✕
                    </button>
                    
                    <button
                      className="alert-action-btn details"
                      onClick={() => console.log('Show alert details:', alert)}
                      title="View Details"
                    >
                      📋
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Emergency Mode Banner */}
      {emergencyMode && alertStats.critical > 0 && (
        <div className="emergency-alert-banner">
          <div className="emergency-content">
            <span className="emergency-icon">🚨</span>
            <span className="emergency-text">
              {alertStats.critical} CRITICAL ALERT{alertStats.critical !== 1 ? 'S' : ''} REQUIRE IMMEDIATE ATTENTION
            </span>
            <button 
              className="emergency-action"
              onClick={() => {
                alerts
                  .filter(a => a.severity === 'critical')
                  .forEach(alert => handleEscalate(alert.id));
              }}
            >
              ESCALATE ALL
            </button>
          </div>
        </div>
      )}

      {/* Real-time indicator */}
      <div className="alerts-realtime-indicator">
        <span className="indicator-dot"></span>
        <span className="indicator-text">Live Alert Monitoring</span>
      </div>
    </div>
  );
};

export default SystemAlertsPanel;
