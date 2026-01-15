// src/components/shared/BusinessObjectiveCard.jsx
import React, { useState, useEffect } from 'react';

const BusinessObjectiveCard = ({
  objective = {},
  progress = 0, // 0-100 percentage
  status = 'active', // 'active', 'completed', 'paused', 'at-risk', 'overdue'
  priority = 'medium', // 'low', 'medium', 'high', 'critical'
  variant = 'default', // 'default', 'minimal', 'detailed', 'compact'
  size = 'medium', // 'small', 'medium', 'large'
  showProgress = true,
  showTimeline = true,
  showMetrics = true,
  showActions = true,
  onClick = null,
  onEdit = null,
  onComplete = null,
  onPause = null,
  className = '',
  realTimeUpdate = false,
  customColor = null,
  ...props
}) => {
  const [currentProgress, setCurrentProgress] = useState(progress);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    if (realTimeUpdate && progress !== currentProgress) {
      setIsUpdating(true);
      const timer = setTimeout(() => {
        setCurrentProgress(progress);
        setIsUpdating(false);
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setCurrentProgress(progress);
    }
  }, [progress, realTimeUpdate, currentProgress]);

  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
        return {
          color: '#28a745',
          icon: 'fas fa-check-circle',
          label: 'Completed',
          bgColor: 'rgba(40, 167, 69, 0.1)'
        };
      case 'at-risk':
        return {
          color: '#ffc107',
          icon: 'fas fa-exclamation-triangle',
          label: 'At Risk',
          bgColor: 'rgba(255, 193, 7, 0.1)'
        };
      case 'overdue':
        return {
          color: '#dc3545',
          icon: 'fas fa-clock',
          label: 'Overdue',
          bgColor: 'rgba(220, 53, 69, 0.1)'
        };
      case 'paused':
        return {
          color: '#6c757d',
          icon: 'fas fa-pause-circle',
          label: 'Paused',
          bgColor: 'rgba(108, 117, 125, 0.1)'
        };
      case 'active':
        return {
          color: '#17a2b8',
          icon: 'fas fa-play-circle',
          label: 'Active',
          bgColor: 'rgba(23, 162, 184, 0.1)'
        };
      default:
        return {
          color: '#6c757d',
          icon: 'fas fa-question-circle',
          label: 'Unknown',
          bgColor: 'rgba(108, 117, 125, 0.1)'
        };
    }
  };

  const getPriorityConfig = () => {
    switch (priority) {
      case 'critical':
        return {
          color: '#dc3545',
          label: 'Critical',
          border: '2px solid #dc3545'
        };
      case 'high':
        return {
          color: '#fd7e14',
          label: 'High',
          border: '2px solid #fd7e14'
        };
      case 'medium':
        return {
          color: '#ffc107',
          label: 'Medium',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        };
      case 'low':
        return {
          color: '#28a745',
          label: 'Low',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        };
      default:
        return {
          color: '#6c757d',
          label: 'Unknown',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        };
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getDaysRemaining = () => {
    if (!objective.deadline) return null;
    const now = new Date();
    const deadline = new Date(objective.deadline);
    const diffTime = deadline - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getProgressColor = () => {
    if (customColor) return customColor;
    if (currentProgress >= 80) return '#28a745';
    if (currentProgress >= 60) return '#17a2b8';
    if (currentProgress >= 40) return '#ffc107';
    return '#dc3545';
  };

  const statusConfig = getStatusConfig();
  const priorityConfig = getPriorityConfig();
  const daysRemaining = getDaysRemaining();

  const cardClasses = [
    'business-objective-card',
    `status-${status}`,
    `priority-${priority}`,
    `variant-${variant}`,
    `size-${size}`,
    isUpdating ? 'updating' : '',
    onClick ? 'clickable' : '',
    className
  ].filter(Boolean).join(' ');

  if (variant === 'minimal') {
    return (
      <div 
        className={cardClasses}
        onClick={onClick}
        style={{ 
          '--status-color': statusConfig.color,
          '--priority-border': priorityConfig.border
        }}
        {...props}
      >
        <div className="minimal-content">
          <div className="minimal-header">
            <i className={statusConfig.icon} style={{ color: statusConfig.color }}></i>
            <span className="minimal-title">{objective.title || 'Untitled Objective'}</span>
            <span className="minimal-progress">{Math.round(currentProgress)}%</span>
          </div>
          {showProgress && (
            <div className="minimal-progress-bar">
              <div 
                className="minimal-progress-fill"
                style={{ 
                  width: `${currentProgress}%`,
                  backgroundColor: getProgressColor()
                }}
              />
            </div>
          )}
        </div>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div 
        className={cardClasses}
        onClick={onClick}
        style={{ 
          '--status-color': statusConfig.color,
          '--priority-border': priorityConfig.border
        }}
        {...props}
      >
        <div className="compact-content">
          <div className="compact-left">
            <div className="compact-status">
              <i className={statusConfig.icon} style={{ color: statusConfig.color }}></i>
            </div>
            <div className="compact-info">
              <h4 className="compact-title">{objective.title || 'Untitled Objective'}</h4>
              <span className="compact-meta">
                {priorityConfig.label} • {daysRemaining ? `${daysRemaining}d left` : 'No deadline'}
              </span>
            </div>
          </div>
          <div className="compact-right">
            <span className="compact-progress-text">{Math.round(currentProgress)}%</span>
            {showProgress && (
              <div className="compact-progress-circle">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <circle
                    cx="20"
                    cy="20"
                    r="16"
                    stroke="rgba(255, 255, 255, 0.2)"
                    strokeWidth="3"
                    fill="transparent"
                  />
                  <circle
                    cx="20"
                    cy="20"
                    r="16"
                    stroke={getProgressColor()}
                    strokeWidth="3"
                    fill="transparent"
                    strokeDasharray={100.53}
                    strokeDashoffset={100.53 - (currentProgress / 100) * 100.53}
                    strokeLinecap="round"
                    transform="rotate(-90 20 20)"
                  />
                </svg>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={cardClasses}
      onClick={onClick}
      style={{ 
        '--status-color': statusConfig.color,
        '--priority-border': priorityConfig.border,
        '--status-bg': statusConfig.bgColor
      }}
      {...props}
    >
      {/* Header */}
      <div className="objective-header">
        <div className="objective-main">
          <div className="objective-status">
            <i className={statusConfig.icon} style={{ color: statusConfig.color }}></i>
            <span className="status-label" style={{ color: statusConfig.color }}>
              {statusConfig.label}
            </span>
          </div>
          <div className="objective-priority">
            <span 
              className="priority-badge"
              style={{ 
                color: priorityConfig.color,
                backgroundColor: `${priorityConfig.color}20`
              }}
            >
              {priorityConfig.label}
            </span>
          </div>
        </div>
        {objective.id && (
          <span className="objective-id">#{objective.id}</span>
        )}
      </div>

      {/* Title and Description */}
      <div className="objective-content">
        <h3 className="objective-title">{objective.title || 'Untitled Objective'}</h3>
        {objective.description && variant === 'detailed' && (
          <p className="objective-description">{objective.description}</p>
        )}
      </div>

      {/* Progress Section */}
      {showProgress && (
        <div className="objective-progress">
          <div className="progress-header">
            <span className="progress-label">Progress</span>
            <span className="progress-percentage">{Math.round(currentProgress)}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ 
                width: `${currentProgress}%`,
                backgroundColor: getProgressColor()
              }}
            />
          </div>
        </div>
      )}

      {/* Timeline */}
      {showTimeline && (objective.startDate || objective.deadline) && (
        <div className="objective-timeline">
          <div className="timeline-item">
            <i className="fas fa-calendar-alt"></i>
            <span className="timeline-label">Start:</span>
            <span className="timeline-value">{formatDate(objective.startDate)}</span>
          </div>
          <div className="timeline-item">
            <i className="fas fa-flag-checkered"></i>
            <span className="timeline-label">Deadline:</span>
            <span className="timeline-value">
              {formatDate(objective.deadline)}
              {daysRemaining !== null && (
                <span className={`days-remaining ${daysRemaining < 0 ? 'overdue' : daysRemaining < 7 ? 'urgent' : ''}`}>
                  ({daysRemaining < 0 ? `${Math.abs(daysRemaining)}d overdue` : `${daysRemaining}d left`})
                </span>
              )}
            </span>
          </div>
        </div>
      )}

      {/* Metrics */}
      {showMetrics && variant === 'detailed' && (
        <div className="objective-metrics">
          <div className="metric-item">
            <span className="metric-label">Owner</span>
            <span className="metric-value">{objective.owner || 'Unassigned'}</span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Department</span>
            <span className="metric-value">{objective.department || 'General'}</span>
          </div>
          {objective.budget && (
            <div className="metric-item">
              <span className="metric-label">Budget</span>
              <span className="metric-value">${objective.budget.toLocaleString()}</span>
            </div>
          )}
          {objective.milestones && (
            <div className="metric-item">
              <span className="metric-label">Milestones</span>
              <span className="metric-value">
                {objective.milestones.filter(m => m.completed).length} / {objective.milestones.length}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      {showActions && (
        <div className="objective-actions">
          {status !== 'completed' && onComplete && (
            <button 
              className="action-btn complete-btn"
              onClick={(e) => {
                e.stopPropagation();
                onComplete(objective);
              }}
            >
              <i className="fas fa-check"></i>
              Complete
            </button>
          )}
          {status === 'active' && onPause && (
            <button 
              className="action-btn pause-btn"
              onClick={(e) => {
                e.stopPropagation();
                onPause(objective);
              }}
            >
              <i className="fas fa-pause"></i>
              Pause
            </button>
          )}
          {onEdit && (
            <button 
              className="action-btn edit-btn"
              onClick={(e) => {
                e.stopPropagation();
                onEdit(objective);
              }}
            >
              <i className="fas fa-edit"></i>
              Edit
            </button>
          )}
          <button className="action-btn view-btn">
            <i className="fas fa-eye"></i>
            View
          </button>
        </div>
      )}
    </div>
  );
};

export default BusinessObjectiveCard;
