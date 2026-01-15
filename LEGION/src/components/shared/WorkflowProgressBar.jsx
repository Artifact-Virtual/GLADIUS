// src/components/shared/WorkflowProgressBar.jsx
import React, { useState, useEffect, useRef } from 'react';

const WorkflowProgressBar = ({
  steps = [],
  currentStep = 0,
  progress = 0, // 0-100 percentage within current step
  status = 'running', // 'pending', 'running', 'completed', 'failed', 'paused'
  variant = 'default', // 'default', 'minimal', 'detailed', 'circular'
  size = 'medium', // 'small', 'medium', 'large'
  showLabels = true,
  showProgress = true,
  showTime = true,
  animated = true,
  onClick = null,
  onStepClick = null,
  className = '',
  estimatedTime = null,
  elapsedTime = null,
  remainingTime = null,
  workflowId = null,
  workflowName = null,
  autoProgress = false,
  progressSpeed = 1000, // ms for auto progress
  ...props
}) => {
  const [internalProgress, setInternalProgress] = useState(progress);
  const [internalCurrentStep, setInternalCurrentStep] = useState(currentStep);
  const [isAnimating, setIsAnimating] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (autoProgress && status === 'running') {
      intervalRef.current = setInterval(() => {
        setInternalProgress(prev => {
          if (prev >= 100) {
            setInternalCurrentStep(prevStep => {
              if (prevStep < steps.length - 1) {
                return prevStep + 1;
              }
              return prevStep;
            });
            return 0;
          }
          return prev + (100 / (progressSpeed / 100));
        });
      }, 100);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoProgress, status, progressSpeed]);

  useEffect(() => {
    if (!autoProgress) {
      setInternalProgress(progress);
      setInternalCurrentStep(currentStep);
    }
  }, [progress, currentStep, autoProgress]);

  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
        return {
          color: '#28a745',
          icon: 'fas fa-check-circle',
          label: 'Completed'
        };
      case 'failed':
        return {
          color: '#dc3545',
          icon: 'fas fa-times-circle',
          label: 'Failed'
        };
      case 'paused':
        return {
          color: '#ffc107',
          icon: 'fas fa-pause-circle',
          label: 'Paused'
        };
      case 'running':
        return {
          color: '#17a2b8',
          icon: 'fas fa-play-circle',
          label: 'Running'
        };
      case 'pending':
        return {
          color: '#6c757d',
          icon: 'fas fa-clock',
          label: 'Pending'
        };
      default:
        return {
          color: '#6c757d',
          icon: 'fas fa-question-circle',
          label: 'Unknown'
        };
    }
  };

  const getStepStatus = (stepIndex) => {
    if (stepIndex < internalCurrentStep) return 'completed';
    if (stepIndex === internalCurrentStep) {
      if (status === 'failed') return 'failed';
      if (status === 'paused') return 'paused';
      return 'active';
    }
    return 'pending';
  };

  const getStepProgress = (stepIndex) => {
    if (stepIndex < internalCurrentStep) return 100;
    if (stepIndex === internalCurrentStep) return internalProgress;
    return 0;
  };

  const formatTime = (seconds) => {
    if (!seconds && seconds !== 0) return '--';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getTotalProgress = () => {
    if (steps.length === 0) return 0;
    const stepProgress = (internalCurrentStep / steps.length) * 100;
    const currentStepProgress = (internalProgress / steps.length);
    return stepProgress + currentStepProgress;
  };

  const statusConfig = getStatusConfig();

  const containerClasses = [
    'workflow-progress-bar',
    `variant-${variant}`,
    `size-${size}`,
    `status-${status}`,
    animated ? 'animated' : '',
    isAnimating ? 'animating' : '',
    onClick ? 'clickable' : '',
    className
  ].filter(Boolean).join(' ');

  if (variant === 'circular') {
    const radius = size === 'small' ? 30 : size === 'large' ? 50 : 40;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (getTotalProgress() / 100) * circumference;

    return (
      <div 
        className={containerClasses}
        onClick={onClick}
        style={{ '--status-color': statusConfig.color }}
        {...props}
      >
        <div className="circular-progress">
          <svg width={(radius + 10) * 2} height={(radius + 10) * 2}>
            <circle
              cx={radius + 10}
              cy={radius + 10}
              r={radius}
              stroke="rgba(255, 255, 255, 0.2)"
              strokeWidth="4"
              fill="transparent"
            />
            <circle
              cx={radius + 10}
              cy={radius + 10}
              r={radius}
              stroke={statusConfig.color}
              strokeWidth="4"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform={`rotate(-90 ${radius + 10} ${radius + 10})`}
              className={animated ? 'progress-circle-animated' : ''}
            />
          </svg>
          <div className="circular-content">
            <i className={statusConfig.icon} style={{ color: statusConfig.color }}></i>
            <span className="circular-percentage">{Math.round(getTotalProgress())}%</span>
            {workflowName && <span className="circular-name">{workflowName}</span>}
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'minimal') {
    return (
      <div 
        className={containerClasses}
        onClick={onClick}
        style={{ '--status-color': statusConfig.color }}
        {...props}
      >
        <div className="minimal-header">
          <span className="minimal-label">
            {workflowName || 'Workflow Progress'}
          </span>
          <span className="minimal-percentage">{Math.round(getTotalProgress())}%</span>
        </div>
        <div className="minimal-progress-bar">
          <div 
            className="minimal-progress-fill"
            style={{ 
              width: `${getTotalProgress()}%`,
              backgroundColor: statusConfig.color
            }}
          />
        </div>
      </div>
    );
  }

  return (
    <div 
      className={containerClasses}
      onClick={onClick}
      style={{ '--status-color': statusConfig.color }}
      {...props}
    >
      {/* Header */}
      <div className="workflow-header">
        <div className="workflow-info">
          <div className="workflow-title">
            <i className={statusConfig.icon} style={{ color: statusConfig.color }}></i>
            <span>{workflowName || 'Workflow Progress'}</span>
          </div>
          {workflowId && (
            <span className="workflow-id">ID: {workflowId}</span>
          )}
        </div>
        <div className="workflow-status">
          <span className="status-label" style={{ color: statusConfig.color }}>
            {statusConfig.label}
          </span>
          {showProgress && (
            <span className="overall-progress">
              {Math.round(getTotalProgress())}%
            </span>
          )}
        </div>
      </div>

      {/* Time Information */}
      {showTime && (elapsedTime || estimatedTime || remainingTime) && (
        <div className="workflow-time">
          {elapsedTime && (
            <span className="time-item">
              <i className="fas fa-clock"></i>
              Elapsed: {formatTime(elapsedTime)}
            </span>
          )}
          {remainingTime && (
            <span className="time-item">
              <i className="fas fa-hourglass-half"></i>
              Remaining: {formatTime(remainingTime)}
            </span>
          )}
          {estimatedTime && (
            <span className="time-item">
              <i className="fas fa-calendar-alt"></i>
              Total: {formatTime(estimatedTime)}
            </span>
          )}
        </div>
      )}

      {/* Progress Steps */}
      <div className="workflow-steps">
        {steps.map((step, index) => {
          const stepStatus = getStepStatus(index);
          const stepProgress = getStepProgress(index);
          
          return (
            <div 
              key={index}
              className={`workflow-step step-${stepStatus}`}
              onClick={() => onStepClick && onStepClick(index, step)}
            >
              {/* Step Indicator */}
              <div className="step-indicator">
                <div className="step-number">
                  {stepStatus === 'completed' ? (
                    <i className="fas fa-check"></i>
                  ) : stepStatus === 'failed' ? (
                    <i className="fas fa-times"></i>
                  ) : (
                    index + 1
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className="step-connector">
                    <div 
                      className="connector-fill"
                      style={{ 
                        width: stepStatus === 'completed' ? '100%' : '0%'
                      }}
                    />
                  </div>
                )}
              </div>

              {/* Step Content */}
              {showLabels && (
                <div className="step-content">
                  <div className="step-label">
                    <span className="step-title">{step.title || step.name || `Step ${index + 1}`}</span>
                    {step.description && variant === 'detailed' && (
                      <span className="step-description">{step.description}</span>
                    )}
                  </div>
                  {stepStatus === 'active' && showProgress && (
                    <div className="step-progress">
                      <div className="step-progress-bar">
                        <div 
                          className="step-progress-fill"
                          style={{ 
                            width: `${stepProgress}%`,
                            backgroundColor: statusConfig.color
                          }}
                        />
                      </div>
                      <span className="step-percentage">{Math.round(stepProgress)}%</span>
                    </div>
                  )}
                  {step.duration && (
                    <span className="step-duration">
                      {formatTime(step.duration)}
                    </span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Overall Progress Bar */}
      {variant === 'detailed' && (
        <div className="overall-progress-bar">
          <div className="progress-bar-container">
            <div 
              className="progress-bar-fill"
              style={{ 
                width: `${getTotalProgress()}%`,
                backgroundColor: statusConfig.color
              }}
            />
          </div>
          <span className="progress-text">
            Step {internalCurrentStep + 1} of {steps.length}
          </span>
        </div>
      )}
    </div>
  );
};

export default WorkflowProgressBar;
